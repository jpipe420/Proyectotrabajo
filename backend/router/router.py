from fastapi import APIRouter, Response, UploadFile, File
from fastapi.responses import FileResponse
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from schema.user_schema import UserSchema, DataUser
from schema.excel_schema import ConfirmacionCarga
from config.db import engine
from model.users import users
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List
from utils.excel_loader import ExcelLoader
from utils.response_models import (
    success_response, error_response, warning_response,
    NotFoundException, DuplicateException, ValidationException,
    UnauthorizedException
)
from config.logger_config import (
    get_api_logger, get_database_logger, get_excel_logger,
    get_auth_logger, log_db_operation
)
import tempfile
import os
import pandas as pd
from sqlalchemy import text
import time

# Configurar loggers
api_logger = get_api_logger()
db_logger = get_database_logger()
excel_logger = get_excel_logger()
auth_logger = get_auth_logger()

user = APIRouter()


@user.get("/")
def root():
    api_logger.info("Acceso al endpoint raíz del router")
    return success_response(
        message="Router de usuarios funcionando",
        data={"module": "users", "status": "active"}
    )


@user.get("/api/user")
def get_users():
    """Obtiene todos los usuarios"""
    api_logger.info("Solicitud de lista de usuarios")
    start_time = time.time()
    
    try:
        with engine.connect() as conn:
            result = conn.execute(users.select()).fetchall()
            columns = users.columns.keys()
            user_list = [dict(zip(columns, row)) for row in result]
            
            duration = (time.time() - start_time) * 1000
            log_db_operation(
                db_logger, "SELECT", "users", True, 
                f"Total registros: {len(user_list)} | {duration:.2f}ms"
            )
            
            api_logger.info(f"✓ Usuarios obtenidos: {len(user_list)}")
            
            return success_response(
                message=f"Se obtuvieron {len(user_list)} usuarios",
                data=user_list,
                metadata={"execution_time_ms": duration}
            )
    
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_db_operation(db_logger, "SELECT", "users", False, str(e))
        api_logger.error(f"✗ Error obteniendo usuarios: {str(e)}")
        raise


@user.get("/api/user/{user_id}")
def get_user(user_id: str):
    """Obtiene un usuario por ID"""
    api_logger.info(f"Solicitud de usuario con ID: {user_id}")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                users.select().where(users.c.id == user_id)
            ).first()
            
            if not result:
                api_logger.warning(f"Usuario no encontrado: ID {user_id}")
                raise NotFoundException(f"Usuario con ID {user_id} no encontrado")
            
            columns = users.columns.keys()
            user_dict = dict(zip(columns, result))
            
            log_db_operation(db_logger, "SELECT", "users", True, f"ID: {user_id}")
            api_logger.info(f"✓ Usuario encontrado: {user_dict.get('username')}")
            
            return success_response(
                message="Usuario encontrado",
                data=user_dict
            )
    
    except NotFoundException:
        raise
    except Exception as e:
        log_db_operation(db_logger, "SELECT", "users", False, str(e))
        api_logger.error(f"✗ Error obteniendo usuario {user_id}: {str(e)}")
        raise


@user.post("/api/user", status_code=HTTP_201_CREATED)
def create_user(data_user: UserSchema):
    """Crea un nuevo usuario"""
    api_logger.info(f"Intento de crear usuario: {data_user.username}")
    
    try:
        with engine.connect() as conn:
            # Verificar username duplicado
            existing_username = conn.execute(
                users.select().where(users.c.username == data_user.username)
            ).first()
            
            if existing_username:
                api_logger.warning(f"Username duplicado: {data_user.username}")
                raise DuplicateException(f"El username '{data_user.username}' ya existe")
            
            # Verificar correo duplicado
            existing_email = conn.execute(
                users.select().where(users.c.correo == data_user.correo)
            ).first()
            
            if existing_email:
                api_logger.warning(f"Correo duplicado: {data_user.correo}")
                raise DuplicateException(f"El correo '{data_user.correo}' ya está registrado")
            
            # Crear usuario
            new_user = data_user.model_dump()
            new_user["user_passw"] = generate_password_hash(
                data_user.user_passw, "pbkdf2:sha256:30", 30
            )
            
            conn.execute(users.insert().values(new_user))
            conn.commit()
            
            log_db_operation(
                db_logger, "INSERT", "users", True, 
                f"Username: {data_user.username}"
            )
            api_logger.info(f"✓ Usuario creado exitosamente: {data_user.username}")
            
            return success_response(
                message=f"Usuario '{data_user.username}' creado exitosamente",
                data={"username": data_user.username, "correo": data_user.correo}
            )
    
    except (DuplicateException, ValidationException):
        raise
    except Exception as e:
        log_db_operation(db_logger, "INSERT", "users", False, str(e))
        api_logger.error(f"✗ Error creando usuario: {str(e)}")
        raise


@user.post("/api/user/Login")
def user_login(data_user: DataUser):
    """Login de usuario"""
    auth_logger.info(f"Intento de login: {data_user.username}")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                users.select().where(users.c.username == data_user.username)
            ).first()
            
            if result is None:
                auth_logger.warning(f"Usuario no encontrado: {data_user.username}")
                raise UnauthorizedException("Credenciales inválidas")
            
            check_passw = check_password_hash(result[4], data_user.user_passw)
            
            if not check_passw:
                auth_logger.warning(f"Contraseña incorrecta: {data_user.username}")
                raise UnauthorizedException("Credenciales inválidas")
            
            auth_logger.info(f"✓ Login exitoso: {data_user.username}")
            
            return success_response(
                message="Login exitoso",
                data={
                    "username": data_user.username,
                    "authenticated": True
                }
            )
    
    except UnauthorizedException:
        raise
    except Exception as e:
        auth_logger.error(f"✗ Error en login: {str(e)}")
        raise


@user.put("/api/user/{user_id}")
def update_user(data_update: UserSchema, user_id: str):
    """Actualiza un usuario"""
    api_logger.info(f"Intento de actualizar usuario ID: {user_id}")
    
    try:
        user_id_int = int(user_id)
        
        with engine.connect() as conn:
            # Verificar que existe
            existing = conn.execute(
                users.select().where(users.c.id == user_id_int)
            ).first()
            
            if not existing:
                api_logger.warning(f"Usuario no encontrado para actualizar: ID {user_id}")
                raise NotFoundException(f"Usuario con ID {user_id} no encontrado")
            
            # Actualizar
            encrypt_passw = generate_password_hash(
                data_update.user_passw, "pbkdf2:sha256:30", 30
            )
            
            conn.execute(users.update().values(
                nombre=data_update.nombre,
                username=data_update.username,
                correo=data_update.correo,
                user_passw=encrypt_passw
            ).where(users.c.id == user_id_int))
            conn.commit()
            
            # Obtener datos actualizados
            result = conn.execute(
                users.select().where(users.c.id == user_id_int)
            ).first()
            
            user_dict = {
                "id": result.id,
                "nombre": result.nombre,
                "username": result.username,
                "correo": result.correo
            }
            
            log_db_operation(
                db_logger, "UPDATE", "users", True, 
                f"ID: {user_id} | Username: {data_update.username}"
            )
            api_logger.info(f"✓ Usuario actualizado: ID {user_id}")
            
            return success_response(
                message="Usuario actualizado exitosamente",
                data=user_dict
            )
    
    except (NotFoundException, ValueError):
        raise
    except Exception as e:
        log_db_operation(db_logger, "UPDATE", "users", False, str(e))
        api_logger.error(f"✗ Error actualizando usuario {user_id}: {str(e)}")
        raise


@user.delete("/api/user/{user_id}", status_code=HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    """Elimina un usuario"""
    api_logger.info(f"Intento de eliminar usuario ID: {user_id}")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                users.delete().where(users.c.id == user_id)
            )
            conn.commit()
            
            if result.rowcount == 0:
                api_logger.warning(f"Usuario no encontrado para eliminar: ID {user_id}")
                raise NotFoundException(f"Usuario con ID {user_id} no encontrado")
            
            log_db_operation(db_logger, "DELETE", "users", True, f"ID: {user_id}")
            api_logger.info(f"✓ Usuario eliminado: ID {user_id}")
            
            return Response(status_code=HTTP_204_NO_CONTENT)
    
    except NotFoundException:
        raise
    except Exception as e:
        log_db_operation(db_logger, "DELETE", "users", False, str(e))
        api_logger.error(f"✗ Error eliminando usuario {user_id}: {str(e)}")
        raise


# ============================================================================
# ENDPOINTS PARA CARGA MASIVA CON PREVIEW
# ============================================================================

@user.post("/api/user/upload/excel/analyze")
async def analyze_excel(file: UploadFile = File(...)):
    """Analiza el archivo Excel y retorna información detallada"""
    excel_logger.info(f"Análisis de archivo Excel: {file.filename}")
    start_time = time.time()
    
    try:
        if not ExcelLoader.allowed_file(file.filename):
            excel_logger.warning(f"Tipo de archivo no permitido: {file.filename}")
            raise ValidationException(
                "Solo se permiten archivos .xlsx o .xls",
                errors=[f"Archivo recibido: {file.filename}"]
            )
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        excel_logger.debug(f"Archivo guardado temporalmente: {temp_file_path}")
        
        try:
            # Obtener info de hojas
            success_info, sheet_info, msg_info = ExcelLoader.get_sheet_info(temp_file_path)
            
            if not success_info:
                excel_logger.error(f"Error obteniendo info de hojas: {msg_info}")
                raise ValidationException(msg_info)
            
            excel_logger.info(
                f"Archivo con {sheet_info['total_sheets']} hoja(s): "
                f"{', '.join(sheet_info['sheet_names'])}"
            )
            
            hojas_validas = []
            hojas_invalidas = []
            
            # Procesar cada hoja
            for nombre_hoja in sheet_info['sheet_names']:
                excel_logger.debug(f"Procesando hoja: {nombre_hoja}")
                
                hoja_data = {
                    "nombre_hoja": nombre_hoja,
                    "total_filas": sheet_info['rows_per_sheet'].get(nombre_hoja, 0),
                    "es_valida": False,
                    "datos": [],
                    "errores": [],
                    "total_validos": 0,
                    "total_duplicados": 0
                }
                
                # Leer hoja
                success, datos, msg = ExcelLoader.read_excel(
                    temp_file_path,
                    sheet_name=nombre_hoja,
                    validate_single_sheet=False
                )
                
                if success and datos:
                    # Validar contra BD
                    with engine.connect() as conn:
                        datos_procesados = []
                        total_validos = 0
                        total_duplicados = 0
                        
                        for idx, usuario_data in enumerate(datos, 1):
                            registro = {
                                'nombre': usuario_data['nombre'],
                                'username': usuario_data['username'],
                                'correo': usuario_data['correo'],
                                'user_passw': usuario_data['user_passw'],
                                'fila_original': idx,
                                'estado_validacion': 'valido',
                                'mensaje_validacion': ''
                            }
                            
                            # Verificar duplicados en BD
                            resultado_username = conn.execute(
                                users.select().where(
                                    users.c.username == usuario_data['username']
                                )
                            ).first()
                            
                            if resultado_username:
                                registro['estado_validacion'] = 'duplicado_bd'
                                registro['mensaje_validacion'] = "Username ya existe en BD"
                                total_duplicados += 1
                            else:
                                resultado_correo = conn.execute(
                                    users.select().where(
                                        users.c.correo == usuario_data['correo']
                                    )
                                ).first()
                                
                                if resultado_correo:
                                    registro['estado_validacion'] = 'duplicado_bd'
                                    registro['mensaje_validacion'] = "Correo ya existe en BD"
                                    total_duplicados += 1
                                else:
                                    total_validos += 1
                            
                            datos_procesados.append(registro)
                    
                    hoja_data['es_valida'] = True
                    hoja_data['datos'] = datos_procesados
                    hoja_data['total_validos'] = total_validos
                    hoja_data['total_duplicados'] = total_duplicados
                    hojas_validas.append(hoja_data)
                    
                    excel_logger.info(
                        f"✓ Hoja '{nombre_hoja}' procesada: "
                        f"{total_validos} válidos, {total_duplicados} duplicados"
                    )
                else:
                    hoja_data['errores'] = [msg]
                    hojas_invalidas.append(hoja_data)
                    excel_logger.warning(f"✗ Hoja '{nombre_hoja}' inválida: {msg}")
            
            duration = (time.time() - start_time) * 1000
            
            total_validos = sum(h['total_validos'] for h in hojas_validas)
            total_duplicados = sum(h['total_duplicados'] for h in hojas_validas)
            
            excel_logger.info(
                f"✓ Análisis completado en {duration:.2f}ms | "
                f"Hojas válidas: {len(hojas_validas)} | "
                f"Registros válidos: {total_validos} | "
                f"Duplicados: {total_duplicados}"
            )
            
            return success_response(
                message=f"Análisis completado: {len(hojas_validas)} hoja(s) válida(s)",
                data={
                    "nombre_archivo": file.filename,
                    "total_hojas": sheet_info['total_sheets'],
                    "hojas_validas": hojas_validas,
                    "hojas_invalidas": hojas_invalidas,
                    "resumen": {
                        "hojas_procesables": len(hojas_validas),
                        "hojas_con_errores": len(hojas_invalidas),
                        "total_registros_validos": total_validos,
                        "total_registros_duplicados": total_duplicados
                    }
                },
                metadata={"execution_time_ms": duration}
            )
            
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                excel_logger.debug("Archivo temporal eliminado")
    
    except (ValidationException, ValueError):
        raise
    except Exception as e:
        excel_logger.error(f"✗ Error analizando Excel: {str(e)}")
        raise


@user.post("/api/user/upload/excel/confirm")
async def confirm_excel_upload(datos: ConfirmacionCarga):
    """Confirma y guarda los registros seleccionados"""
    excel_logger.info(f"Confirmación de carga: {len(datos.registros)} registros")
    start_time = time.time()
    
    try:
        registros = datos.registros
        
        if not registros:
            excel_logger.warning("No se recibieron registros para guardar")
            raise ValidationException("No se recibieron registros para guardar")
        
        usuarios_creados = 0
        errores = []
        
        with engine.connect() as conn:
            for idx, usuario_data in enumerate(registros, 1):
                try:
                    # Validar campos
                    campos_requeridos = ['nombre', 'username', 'correo', 'user_passw']
                    if not all(k in usuario_data for k in campos_requeridos):
                        error_msg = f"Registro {idx}: Faltan campos requeridos"
                        errores.append(error_msg)
                        excel_logger.warning(error_msg)
                        continue
                    
                    # Verificar duplicados
                    resultado_username = conn.execute(
                        users.select().where(
                            users.c.username == usuario_data['username']
                        )
                    ).first()
                    
                    if resultado_username:
                        error_msg = f"Registro {idx}: Username '{usuario_data['username']}' ya existe"
                        errores.append(error_msg)
                        excel_logger.warning(error_msg)
                        continue
                    
                    resultado_correo = conn.execute(
                        users.select().where(
                            users.c.correo == usuario_data['correo']
                        )
                    ).first()
                    
                    if resultado_correo:
                        error_msg = f"Registro {idx}: Correo '{usuario_data['correo']}' ya existe"
                        errores.append(error_msg)
                        excel_logger.warning(error_msg)
                        continue
                    
                    # Encriptar y guardar
                    password_encriptada = generate_password_hash(
                        str(usuario_data['user_passw']),
                        "pbkdf2:sha256:30",
                        30
                    )
                    
                    nuevo_usuario = {
                        'nombre': str(usuario_data['nombre']).strip(),
                        'username': str(usuario_data['username']).strip(),
                        'correo': str(usuario_data['correo']).strip(),
                        'user_passw': password_encriptada
                    }
                    
                    conn.execute(users.insert().values(nuevo_usuario))
                    usuarios_creados += 1
                    excel_logger.debug(f"Usuario creado: {nuevo_usuario['username']}")
                    
                except Exception as e:
                    error_msg = f"Registro {idx}: {str(e)}"
                    errores.append(error_msg)
                    excel_logger.error(error_msg)
            
            conn.commit()
        
        duration = (time.time() - start_time) * 1000
        
        log_db_operation(
            db_logger, "INSERT_BULK", "users", True,
            f"{usuarios_creados} usuarios creados | {duration:.2f}ms"
        )
        
        excel_logger.info(
            f"✓ Carga completada: {usuarios_creados}/{len(registros)} usuarios creados"
        )
        
        if errores:
            return warning_response(
                message=f"Se guardaron {usuarios_creados} usuarios con {len(errores)} error(es)",
                data={
                    "usuarios_creados": usuarios_creados,
                    "total_procesados": len(registros),
                    "tasa_exito": f"{(usuarios_creados/len(registros)*100):.1f}%"
                },
                warnings=errores,
                metadata={"execution_time_ms": duration}
            )
        
        return success_response(
            message=f"Se guardaron {usuarios_creados} usuarios exitosamente",
            data={
                "usuarios_creados": usuarios_creados,
                "total_procesados": len(registros),
                "tasa_exito": "100%"
            },
            metadata={"execution_time_ms": duration}
        )
    
    except ValidationException:
        raise
    except Exception as e:
        excel_logger.error(f"✗ Error confirmando carga: {str(e)}")
        raise


@user.get("/api/user/statistics")
async def get_user_statistics():
    """Obtiene estadísticas de usuarios"""
    api_logger.info("Solicitud de estadísticas de usuarios")
    start_time = time.time()
    
    try:
        with engine.connect() as conn:
            # Total usuarios
            total_query = text("SELECT COUNT(*) FROM users")
            total_usuarios = conn.execute(total_query).scalar()
            
            # Por mes
            usuarios_por_mes_query = text("""
                SELECT 
                    DATE_FORMAT(created_at, '%Y-%m') as mes,
                    DATE_FORMAT(created_at, '%M %Y') as mes_nombre,
                    COUNT(*) as cantidad
                FROM users
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                GROUP BY DATE_FORMAT(created_at, '%Y-%m'), mes_nombre
                ORDER BY mes
            """)
            resultado_meses = conn.execute(usuarios_por_mes_query).fetchall()
            usuarios_por_mes = [
                {"mes": row[0], "mes_nombre": row[1], "cantidad": row[2]} 
                for row in resultado_meses
            ]
            
            # Por dominio
            usuarios_por_dominio_query = text("""
                SELECT 
                    SUBSTRING_INDEX(correo, '@', -1) as dominio,
                    COUNT(*) as cantidad
                FROM users
                GROUP BY dominio
                ORDER BY cantidad DESC
                LIMIT 10
            """)
            resultado_dominios = conn.execute(usuarios_por_dominio_query).fetchall()
            usuarios_por_dominio = [
                {"dominio": row[0], "cantidad": row[1]} 
                for row in resultado_dominios
            ]
            
            # Resumen temporal
            resumen_temporal_query = text("""
                SELECT 
                    SUM(CASE WHEN DATE(created_at) = CURDATE() THEN 1 ELSE 0 END) as hoy,
                    SUM(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as semana,
                    SUM(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) as mes
                FROM users
            """)
            resultado_temporal = conn.execute(resumen_temporal_query).first()
            resumen_temporal = {
                "hoy": resultado_temporal[0] or 0,
                "esta_semana": resultado_temporal[1] or 0,
                "este_mes": resultado_temporal[2] or 0
            }
            
            duration = (time.time() - start_time) * 1000
            
            api_logger.info(f"✓ Estadísticas generadas en {duration:.2f}ms")
            
            return success_response(
                message="Estadísticas obtenidas exitosamente",
                data={
                    "total_usuarios": total_usuarios,
                    "resumen_temporal": resumen_temporal,
                    "usuarios_por_mes": usuarios_por_mes,
                    "usuarios_por_dominio": usuarios_por_dominio
                },
                metadata={"execution_time_ms": duration}
            )
    
    except Exception as e:
        api_logger.error(f"✗ Error obteniendo estadísticas: {str(e)}")
        raise


@user.get("/api/user/template/excel")
async def descargar_template():
    """Descarga plantilla de Excel"""
    excel_logger.info("Solicitud de descarga de plantilla Excel")
    
    try:
        datos_usuarios = {
            'nombre': ['Juan Pérez', 'María García', 'Carlos López'],
            'username': ['juanperez', 'mariagarcia', 'carloslopez'],
            'correo': ['juan@gmail.com', 'maria@gmail.com', 'carlos@gmail.com'],
            'user_passw': ['password123', 'password456', 'password789']
        }
        
        datos_vendedores = {
            'nombre': ['Pedro Vendedor', 'Ana Comercial'],
            'username': ['pvendedor', 'acomercial'],
            'correo': ['pedro@empresa.com', 'ana@empresa.com'],
            'user_passw': ['vendedor123', 'comercial456']
        }
        
        datos_clientes = {
            'nombre': ['Cliente Uno', 'Cliente Dos'],
            'username': ['cliente1', 'cliente2'],
            'correo': ['cliente1@mail.com', 'cliente2@mail.com'],
            'user_passw': ['cliente123', 'cliente456']
        }
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
                pd.DataFrame(datos_usuarios).to_excel(
                    writer, sheet_name='Usuarios', index=False
                )
                pd.DataFrame(datos_vendedores).to_excel(
                    writer, sheet_name='Vendedores', index=False
                )
                pd.DataFrame(datos_clientes).to_excel(
                    writer, sheet_name='Clientes', index=False
                )
            
            temp_file_path = temp_file.name
        
        excel_logger.info("✓ Plantilla generada exitosamente")
        
        return FileResponse(
            temp_file_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename='plantilla_usuarios_multihojas.xlsx',
            background=None
        )
    
    except Exception as e:
        excel_logger.error(f"✗ Error generando plantilla: {str(e)}")
        raise


@user.get("/api/user/excel/requirements")
async def get_excel_requirements():
    """Información sobre requisitos del Excel"""
    api_logger.debug("Solicitud de requisitos de Excel")
    
    return success_response(
        message="Requisitos del archivo Excel",
        data={
            "formato_archivo": [".xlsx", ".xls"],
            "columnas_requeridas": ["nombre", "username", "correo", "user_passw"],
            "validaciones": {
                "nombre": "No puede estar vacío",
                "username": {
                    "longitud_minima": 3,
                    "unico": True,
                    "descripcion": "Mínimo 3 caracteres, único en el sistema"
                },
                "correo": {
                    "formato": "email válido",
                    "unico": True,
                    "descripcion": "Formato válido, único en el sistema"
                },
                "user_passw": {
                    "longitud_minima": 6,
                    "descripcion": "Mínimo 6 caracteres"
                }
            },
            "notas": [
                "El archivo puede contener múltiples hojas",
                "Solo se procesarán hojas con la estructura correcta",
                "Los duplicados serán detectados automáticamente",
                "Podrás editar los datos antes de confirmar la carga"
            ],
            "ejemplo": {
                "nombre": "Juan Pérez",
                "username": "juanperez",
                "correo": "juan@gmail.com",
                "user_passw": "mipassword123"
            }
        }
    )