from pydantic import BaseModel

class ProductoBase(BaseModel):
    nombre: str
    descripcion_tecnica: str

class ProductoCreate(ProductoBase):
    pass

class ProductoDB(ProductoBase):
    id: int

    class Config:
        orm_mode = True
