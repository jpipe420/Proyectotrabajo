# router/products_router.py

from fastapi import APIRouter, Response, HTTPException, status
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from typing import List

# Importamos la conexión a la BD
from config.db import engine
# Importaciones ABSOLUTAS que ahora funcionan gracias a PYTHONPATH
from model.products import products 
from schema.product_schema import ProductSchema, ProductCreate, ProductUpdate

# Definimos el nuevo router para Productos
product_router = APIRouter()


# ----------------------------------------------------------------------
# CREAR UN NUEVO PRODUCTO (C de CRUD)
# ----------------------------------------------------------------------
@product_router.post(
    "/api/products", 
    response_model=ProductSchema, 
    status_code=status.HTTP_201_CREATED, 
    tags=["Products"]
)
def create_product(product_data: ProductCreate):
    with engine.connect() as conn:
        # 1. Verificar si la referencia ya existe (UNIQUE constraint)
        existing_product = conn.execute(
            products.select().where(products.c.referencia == product_data.referencia)
        ).first()

        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La referencia '{product_data.referencia}' ya está registrada."
            )

        # 2. Insertar el nuevo producto
        new_product = product_data.model_dump() 
        result = conn.execute(products.insert().values(new_product))
        conn.commit()

        # 3. Obtener el registro insertado (incluyendo el ID)
        inserted_product = conn.execute(
            products.select().where(products.c.id == result.lastrowid)
        ).first()
        
        # Devolver el producto insertado
        return inserted_product

# ----------------------------------------------------------------------
# OBTENER TODOS LOS PRODUCTOS (R de CRUD)
# ----------------------------------------------------------------------
@product_router.get("/api/products", response_model=List[ProductSchema], tags=["Products"])
def get_products():
    with engine.connect() as conn:
        result = conn.execute(products.select()).fetchall()
        return [ProductSchema.model_validate(row, from_attributes=True) for row in result]


# ----------------------------------------------------------------------
# OBTENER UN PRODUCTO POR ID (R de CRUD)
# ----------------------------------------------------------------------
@product_router.get("/api/products/{product_id}", response_model=ProductSchema, tags=["Products"])
def get_product(product_id: int):
    with engine.connect() as conn:
        result = conn.execute(
            products.select().where(products.c.id == product_id)
        ).first()
        
        if result is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Devolver el resultado usando el esquema
        return result


# ----------------------------------------------------------------------
# ACTUALIZAR UN PRODUCTO (U de CRUD)
# ----------------------------------------------------------------------
@product_router.put("/api/products/{product_id}", response_model=ProductSchema, tags=["Products"])
def update_product(product_id: int, product_data: ProductUpdate):
    with engine.connect() as conn:
        # 1. Verificar si la nueva referencia (si cambia) ya existe en OTRO producto
        existing_product = conn.execute(
            products.select().where(
                (products.c.referencia == product_data.referencia) & (products.c.id != product_id)
            )
        ).first()

        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La referencia '{product_data.referencia}' ya está registrada en otro producto."
            )

        # 2. Actualizar los datos
        update_values = product_data.model_dump(exclude_unset=True) 
        result = conn.execute(
            products.update().values(update_values).where(products.c.id == product_id)
        )
        conn.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado para actualizar")
        
        # 3. Obtener el producto actualizado para devolver
        updated_product = conn.execute(
            products.select().where(products.c.id == product_id)
        ).first()
        
        return updated_product

# ----------------------------------------------------------------------
# ELIMINAR UN PRODUCTO (D de CRUD)
# ----------------------------------------------------------------------
@product_router.delete("/api/products/{product_id}", status_code=HTTP_204_NO_CONTENT, tags=["Products"])
def delete_product(product_id: int):
    with engine.connect() as conn:
        result = conn.execute(products.delete().where(products.c.id == product_id))
        conn.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado para eliminar")
        
        return Response(status_code=HTTP_204_NO_CONTENT)