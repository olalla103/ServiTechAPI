from typing import Optional
from pydantic import BaseModel

class ProductoBase(BaseModel):
    nombre: str
    descripcion_tecnica: str
    precio: float  # Nuevo campo obligatorio

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion_tecnica: Optional[str] = None
    precio: Optional[float] = None  # Permite actualizar el precio

class ProductoDB(ProductoBase):
    id: int

    class Config:
        orm_mode = True
