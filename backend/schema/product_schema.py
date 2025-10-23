# schema/product_schema.py

from pydantic import BaseModel, Field
from typing import Optional

# Esquema base (usado para crear y actualizar)
class ProductBase(BaseModel):
    nombre: str = Field(..., max_length=255)
    referencia: str = Field(..., max_length=50)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: float = Field(..., gt=0.0)  # Precio debe ser mayor a 0
    stock: int = Field(..., ge=0)     # Stock debe ser mayor o igual a 0

# 1. Esquema para la CREACIÓN de un nuevo producto (Entrada de datos)
class ProductCreate(ProductBase):
    pass # Hereda todos los campos de ProductBase

# 2. Esquema para la ACTUALIZACIÓN de un producto (Entrada de datos)
class ProductUpdate(ProductBase):
    # Aquí podríamos hacer campos opcionales si fuera necesario, 
    # pero mantendremos los mismos que el base por simplicidad del CRUD
    pass

# 3. Esquema del producto COMPLETO (Usado para devolver datos)
class ProductSchema(ProductBase):
    id: Optional[int] = None
    
    class Config:
        from_attributes = True