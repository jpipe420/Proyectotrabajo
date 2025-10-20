from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):
    id: Optional[int] = None
    nombre: str
    username: str
    correo: str
    user_passw: str

    class Config:
        from_attributes = True


class DataUser(BaseModel):
    username: str
    user_passw: str