from fastapi import APIRouter, Response, HTTPException, UploadFile, File
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from schema.user_schema import UserSchema, DataUser
from config.db import engine
from model.users import users
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List
from utils.excel_loader import ExcelLoader
import tempfile
import os


user = APIRouter()

@user.get("/")
def root():
    return {"wenas x2"}


@user.get("/api/user", response_model=List[UserSchema])
def get_users():
    with engine.connect() as conn:
        result = conn.execute(users.select())
        result = conn.execute(users.select()).fetchall()

        # Obtener los nombres de las columnas
        columns = users.columns.keys()

        # Convertir el resultado a una lista de diccionarios
        user_list = [dict(zip(columns, row)) for row in result]

        return user_list



@user.get("/api/user/{user_id}", response_model=UserSchema)
def get_user(user_id: str):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.id == user_id)).first()
        return result


@user.post("/api/user", status_code=HTTP_201_CREATED)
def create_user(data_user: UserSchema):
  with engine.connect() as conn:
    new_user = data_user.model_dump()
    new_user["user_passw"] = generate_password_hash(data_user.user_passw, "pbkdf2:sha256:30", 30)
    conn.execute(users.insert().values(new_user))
    conn.commit()
    return Response(status_code=HTTP_201_CREATED)



@user.post("/api/user/Login")
def user_login(data_user: DataUser):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.username == data_user.username)).first()
        if result != None:
            check_passw = check_password_hash(result[4],data_user.user_passw)
            if check_passw:
               return "Succes"
         
        return "Denied"



@user.put("/api/user/{user_id}")
def update_user(data_update: UserSchema, user_id: str):
    try:
        with engine.connect() as conn:
            # Convertir user_id a entero
            user_id_int = int(user_id)
            
            encrypt_passw = generate_password_hash(data_update.user_passw, "pbkdf2:sha256:30", 30)
            conn.execute(users.update().values(
                nombre=data_update.nombre, 
                username=data_update.username, 
                correo=data_update.correo, 
                user_passw=encrypt_passw
            ).where(users.c.id == user_id_int))
            conn.commit()
            
            result = conn.execute(users.select().where(users.c.id == user_id_int)).first()
            if result:
                user_dict = {
                    "id": result.id,
                    "nombre": result.nombre,
                    "username": result.username,
                    "correo": result.correo
                }
                return user_dict
            else:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except Exception as e:
        print(f"Error en update_user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")
            


@user.delete("/api/user/{user_id}", status_code=HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
 with engine.connect() as conn:
    conn.execute(users.delete().where(users.c.id == user_id))
    conn.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)


@user.post("/api/user/upload/excel")
async def upload_excel(file: UploadFile = File(...)):
    """
    Endpoint para cargar usuarios masivamente desde Excel
    Acepta archivos .xlsx y .xls
    """
    try:
        # Validar tipo de archivo
        if not ExcelLoader.allowed_file(file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Solo se permiten archivos .xlsx o .xls"
            )
        
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        try:
            # Leer y validar el Excel
            es_valido, datos, mensaje = ExcelLoader.read_excel(temp_file_path)
            
            if not es_valido:
                raise HTTPException(status_code=400, detail=mensaje)
            
            # Procesar los datos
            usuarios_creados = 0
            usuarios_duplicados = 0
            errores = []
            
            with engine.connect() as conn:
                for idx, usuario_data in enumerate(datos, 1):
                    try:
                        # Verificar si el usuario ya existe
                        resultado_existente = conn.execute(
                            users.select().where(users.c.username == usuario_data['username'])
                        ).first()
                        
                        if resultado_existente:
                            usuarios_duplicados += 1
                            errores.append(f"Fila {idx}: Usuario '{usuario_data['username']}' ya existe")
                            continue
                        
                        # Encriptar contraseña
                        password_encriptada = generate_password_hash(
                            usuario_data['user_passw'], 
                            "pbkdf2:sha256:30", 
                            30
                        )
                        
                        # Preparar datos para insertar
                        nuevo_usuario = {
                            'nombre': usuario_data['nombre'].strip(),
                            'username': usuario_data['username'].strip(),
                            'correo': usuario_data['correo'].strip(),
                            'user_passw': password_encriptada
                        }
                        
                        # Insertar en la base de datos
                        conn.execute(users.insert().values(nuevo_usuario))
                        usuarios_creados += 1
                        
                    except Exception as e:
                        errores.append(f"Fila {idx}: Error - {str(e)}")
                
                # Confirmar cambios
                conn.commit()
            
            return {
                "exito": True,
                "mensaje": f"Carga completada",
                "usuarios_creados": usuarios_creados,
                "usuarios_duplicados": usuarios_duplicados,
                "errores": errores,
                "total_filas_procesadas": len(datos)
            }
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")
    



@user.get("/api/user/template/excel")
async def descargar_template():
    """
    Endpoint para descargar la plantilla de Excel
    """
    from fastapi.responses import FileResponse
    import pandas as pd
    import tempfile
    
    try:
        # Crear datos de ejemplo
        datos_ejemplo = {
            'nombre': ['Juan Pérez', 'María García'],
            'username': ['juanperez', 'mariagarcia'],
            'correo': ['juan@gmail.com', 'maria@gmail.com'],
            'user_passw': ['password123', 'password456']
        }
        
        df = pd.DataFrame(datos_ejemplo)
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            df.to_excel(temp_file.name, index=False, sheet_name='Usuarios')
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename='plantilla_usuarios.xlsx'
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")