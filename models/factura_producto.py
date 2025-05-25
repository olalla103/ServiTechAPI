from pydantic import BaseModel

class FacturaProductoBase(BaseModel):
    factura_id: int
    producto_id: int

class FacturaProductoCreate(FacturaProductoBase):
    pass

class FacturaProductoDB(FacturaProductoBase):
    class Config:
        orm_mode = True
