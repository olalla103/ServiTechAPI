from typing import Optional

from pydantic import BaseModel

class FacturaProductoBase(BaseModel):
    factura_id: int
    producto_id: int
    cantidad: int  # Nuevo campo obligatorio

class FacturaProductoCreate(FacturaProductoBase):
    pass

class FacturaProductoUpdate(BaseModel):
    cantidad: Optional[int] = None  # Solo permite actualizar la cantidad

class FacturaProductoDB(FacturaProductoBase):
    id: int  # Si tienes un id autoincremental en la tabla

    class Config:
        orm_mode = True
