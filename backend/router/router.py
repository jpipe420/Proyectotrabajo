from fastapi import APIRouter, Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from schema.user_schema import UserSchema, DataUser
from config.db import engine
from model.users import users
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List


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



@user.put("/api/user/{user_id}", response_model=UserSchema)
def update_user(data_update: UserSchema, user_id: str):
  with engine.connect() as conn:
    encrypt_passw = generate_password_hash(data_update.user_passw, "pbkdf2:sha256:30", 30)
    conn.execute(users.update().values(nombre=data_update.nombre, username=data_update.username, correo=data_update.correo, user_passw=encrypt_passw).where(users.c.id == user_id))
    conn.commit()
    result = conn.execute(users.select().where(users.c.id == user_id)).first()
    if result:
            # Convertir manualmente a diccionario
            user_dict = {
                "id": result.id,
                "nombre": result.nombre,
                "username": result.username,
                "correo": result.correo
                # No devolver la contraseña por seguridad
            }
            return user_dict
    else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado después de actualizar")
            


@user.delete("/api/user/{user_id}", status_code=HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
 with engine.connect() as conn:
    conn.execute(users.delete().where(users.c.id == user_id))
    conn.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)
