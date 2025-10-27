from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserSchema(BaseModel):
    id: Optional[int] = None
    nombre: str
    username: str
    correo: str
    user_passw: str
    created_at: Optional[datetime] = None  # ← NUEVO: Fecha de creación
    updated_at: Optional[datetime] = None  # ← NUEVO: Fecha de actualización

    class Config:
        from_attributes = True


class DataUser(BaseModel):
    username: str
    user_passw: str