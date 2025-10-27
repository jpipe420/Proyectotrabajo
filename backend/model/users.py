from sqlalchemy import Table, Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from config.db import engine, meta_data

# Definición de la tabla users
users = Table(
    'users',
    meta_data,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('nombre', String(255), nullable=False),
    Column('username', String(255), unique=True, nullable=False, index=True),
    Column('correo', String(255), unique=True, nullable=False, index=True),
    Column('user_passw', String(255), nullable=False),
    Column('created_at', TIMESTAMP, server_default=func.now(), nullable=True, comment='Fecha de creación'),
    Column('updated_at', TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=True, comment='Fecha de actualización'),
    extend_existing=True
)

# Crear la tabla si no existe
meta_data.create_all(engine)