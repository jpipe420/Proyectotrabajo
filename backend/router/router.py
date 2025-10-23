from fastapi import APIRouter, Response, HTTPException, UploadFile, File, status
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
# --- Importamos TODOS los esquemas ajustados ---
from schema.user_schema import UserSchema, DataUser, UserCreate
# ---------------------------------------------
from config.db import engine
from model.users import users
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List
from utils.excel_loader import ExcelLoader
import tempfile
import os
import json


user = APIRouter()

@user.get("/")
def root():
    return {"wenas x2"}

# ----------------------------------------------------------------------
# OBTENER TODOS LOS USUARIOS
# ----------------------------------------------------------------------
@user.get("/api/user", response_model=List[UserSchema], tags=["Users"])
def get_users():
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()

        # Obtener los nombres de las columnas
        columns = users.columns.keys()

        # Convertir el resultado a una lista de diccionarios
        user_list = [dict(zip(columns, row)) for row in result]

        return user_list

# ----------------------------------------------------------------------
# OBTENER UN USUARIO POR ID
# ----------------------------------------------------------------------
@user.get("/api/user/{user_id}", response_model=UserSchema, tags=["Users"])
def get_user(user_id: str):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.id == user_id)).first()
        if result is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return result

# ----------------------------------------------------------------------
# NUEVO ENDPOINT DE REGISTRO (SIGN-UP)
# Usa el esquema UserCreate para la entrada de datos.
# ----------------------------------------------------------------------
@user.post(
    "/api/user/register", 
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"]
)
def register_user(data_user: UserCreate):
    with engine.connect() as conn:
        # 1. Verificar si el usuario ya existe (por username o correo)
        existing_user = conn.execute(users.select().where(
            (users.c.correo == data_user.correo) | (users.c.username == data_user.username)
        )).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El usuario o correo ya están registrados."
            )

        # 2. Hashear la contraseña (usando el campo 'password' de UserCreate)
        hashed_pass = generate_password_hash(data_user.password, "pbkdf2:sha256:30", 30)

        # 3. Preparar los datos para la inserción
        new_user = {
            "nombre": data_user.nombre,
            "username": data_user.username,
            "correo": data_user.correo,
            "user_passw": hashed_pass # Guardamos el hash en el campo de la BD
        }

        # 4. Insertar el nuevo usuario en la BD
        result = conn.execute(users.insert().values(new_user))
        conn.commit()

        # 5. Obtener el registro insertado para devolver ID
        inserted_user = conn.execute(users.select().where(users.c.id == result.lastrowid)).first()
        
        # Devolver un diccionario simple, excluyendo la contraseña
        user_dict = {
            "id": inserted_user.id,
            "nombre": inserted_user.nombre,
            "username": inserted_user.username,
            "correo": inserted_user.correo
        }
        return user_dict

# ----------------------------------------------------------------------
# ENDPOINT DE LOGIN (AJUSTADO POR SEGURIDAD)
# Usa el esquema DataUser para la entrada de datos.
# ----------------------------------------------------------------------
@user.post("/api/user/Login", tags=["Auth"])
def user_login(data_user: DataUser):
    with engine.connect() as conn:
        # 1. Buscar el usuario por username
        result = conn.execute(users.select().where(users.c.username == data_user.username)).first()
        
        if result is None:
            # Si no encuentra el usuario
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

        # 2. Verificar la contraseña hasheada (usando el campo 'password' de DataUser)
        # El índice 4 es 'user_passw' en la tupla de resultado de la BD
        check_passw = check_password_hash(result[4], data_user.password)
        
        if check_passw:
            # Login Exitoso
            return {"message": "Success"}
         
        # Si la contraseña es incorrecta
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

# ----------------------------------------------------------------------
# ACTUALIZAR USUARIO
# ----------------------------------------------------------------------
@user.put("/api/user/{user_id}", tags=["Users"])
def update_user(data_update: UserSchema, user_id: str):
    try:
        with engine.connect() as conn:
            user_id_int = int(user_id)
            
            # Rehasheamos la contraseña
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
                # Se devuelve el usuario sin la contraseña
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar: {str(e)}")
            
# ----------------------------------------------------------------------
# ELIMINAR USUARIO
# ----------------------------------------------------------------------
@user.delete("/api/user/{user_id}", status_code=HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(user_id: str):
 with engine.connect() as conn:
    conn.execute(users.delete().where(users.c.id == user_id))
    conn.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)

# ----------------------------------------------------------------------
# CARGA DE EXCEL
# ----------------------------------------------------------------------
@user.post("/api/user/upload/excel", tags=["Files"])
async def upload_excel(file: UploadFile = File(...)):
    """
    Endpoint para cargar usuarios masivamente desde Excel
    """
    try:
        if not ExcelLoader.allowed_file(file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Solo se permiten archivos .xlsx o .xls"
            )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        try:
            es_valido, datos, mensaje = ExcelLoader.read_excel(temp_file_path)
            
            if not es_valido:
                raise HTTPException(status_code=400, detail=mensaje)
            
            usuarios_creados = 0
            usuarios_duplicados = 0
            errores = []
            
            with engine.connect() as conn:
                for idx, usuario_data in enumerate(datos, 1):
                    try:
                        resultado_existente = conn.execute(
                            users.select().where(users.c.username == usuario_data['username'])
                        ).first()
                        
                        if resultado_existente:
                            usuarios_duplicados += 1
                            errores.append(f"Fila {idx}: Usuario '{usuario_data['username']}' ya existe")
                            continue
                        
                        password_encriptada = generate_password_hash(
                            usuario_data['user_passw'], 
                            "pbkdf2:sha256:30", 
                            30
                        )
                        
                        nuevo_usuario = {
                            'nombre': usuario_data['nombre'].strip(),
                            'username': usuario_data['username'].strip(),
                            'correo': usuario_data['correo'].strip(),
                            'user_passw': password_encriptada
                        }
                        
                        conn.execute(users.insert().values(nuevo_usuario))
                        usuarios_creados += 1
                        
                    except Exception as e:
                        errores.append(f"Fila {idx}: Error - {str(e)}")
                
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
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en el servidor: {str(e)}")
    
# ----------------------------------------------------------------------
# DESCARGA DE TEMPLATE DE EXCEL
# ----------------------------------------------------------------------
@user.get("/api/user/template/excel", tags=["Files"])
async def descargar_template():
    """
    Endpoint para descargar la plantilla de Excel
    """
    from fastapi.responses import FileResponse
    import pandas as pd
    import tempfile
    
    try:
        datos_ejemplo = {
            'nombre': ['Juan Pérez', 'María García'],
            'username': ['juanperez', 'mariagarcia'],
            'correo': ['juan@gmail.com', 'maria@gmail.com'],
            'user_passw': ['password123', 'password456']
        }
        
        df = pd.DataFrame(datos_ejemplo)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            df.to_excel(temp_file.name, index=False, sheet_name='Usuarios')
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename='plantilla_usuarios.xlsx'
        )
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {str(e)}")