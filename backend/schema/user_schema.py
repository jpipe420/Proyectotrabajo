from pydantic import BaseModel, EmailStr
from typing import Optional

# 1. Esquema para la CREACIÓN/REGISTRO de un nuevo usuario (Entrada de datos)
# Es más limpio que el UserSchema, solo pide los campos necesarios para crear la cuenta.
class UserCreate(BaseModel):
    nombre: str
    username: str
    correo: EmailStr # El correo debe ser un formato válido
    password: str # El usuario envía la contraseña plana aquí

# 2. Esquema del usuario COMPLETO (Usado para la BD y para devolver datos)
# Contiene 'user_passw' porque es el nombre de la columna en la tabla 'users'.
class UserSchema(BaseModel):
    id: Optional[int] = None
    nombre: str
    username: str
    correo: EmailStr
    user_passw: str # Campo para la base de datos (contendrá la contraseña hasheada)

    class Config:
        from_attributes = True

# 3. Esquema para el Login (Entrada de datos)
class DataUser(BaseModel):
    username: str
    password: str # Campo ajustado para la función de login