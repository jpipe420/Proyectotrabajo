# model/Products.py

from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Float
from config.db import engine, meta_data

# Definición de la tabla 'products'
products = Table("products", meta_data,
            Column("id", Integer, primary_key=True),
            Column("nombre", String(255), nullable=False),
            Column("referencia", String(50), nullable=False, unique=True), # Campo único para la referencia
            Column("descripcion", String(500), nullable=True),
            Column("precio", Float, nullable=False),
            Column("stock", Integer, nullable=False) )

# Esto asegura que la nueva tabla 'products' se cree en la BD
meta_data.create_all(engine)