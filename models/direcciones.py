from pydantic import BaseModel
from typing import Optional

class DireccionBase(BaseModel):
    calle: str
    numero: str
    piso: Optional[str] = None
    puerta: Optional[str] = None
    ciudad: str
    cp: str
    provincia: str
    pais: str

class DireccionCreate(DireccionBase):
    pass

class DireccionUpdate(BaseModel):
    calle: Optional[str] = None
    numero: Optional[str] = None
    piso: Optional[str] = None
    puerta: Optional[str] = None
    ciudad: Optional[str] = None
    cp: Optional[str] = None
    provincia: Optional[str] = None
    pais: Optional[str] = None

class DireccionDB(DireccionBase):
    id: int
    usuario_id: int

    class Config:
        orm_mode = True
