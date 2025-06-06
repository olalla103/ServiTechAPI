from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

class FacturaBase(BaseModel):
    fecha_emision: datetime
    tiempo_total: float
    cantidad_total: float
    cantidad_adicional: float
    IVA: float
    observaciones: Optional[str] = None
    tecnico_id: int
    cliente_id: int
    incidencia_id: int

    @field_validator('IVA')
    def iva_positivo(cls, v):
        if v < 0:
            raise ValueError('El IVA debe ser positivo')
        return v

    @field_validator('tiempo_total')
    def tiempo_total_positivo(cls, v):
        if v < 0:
            raise ValueError('El tiempo total debe ser positivo')
        return v

    @field_validator('cantidad_total')
    def cantidad_total_positiva(cls, v):
        if v < 0:
            raise ValueError('La cantidad total debe ser positiva')
        return v

    @field_validator('cantidad_adicional')
    def cantidad_adicional_positiva(cls, v):
        if v < 0:
            raise ValueError('La cantidad adicional debe ser positiva')
        return v

class ProductoEnFactura(BaseModel):
    producto_id: int
    cantidad: int


class FacturaCreate(BaseModel):
    fecha_emision: Optional[datetime] = None
    tiempo_total: Optional[float] = None
    cantidad_total: Optional[float] = None
    cantidad_adicional: Optional[float] = None
    IVA: Optional[float] = 0.0
    observaciones: Optional[str] = None
    tecnico_id: int
    cliente_id: int
    incidencia_id: int
    productos: Optional[List[ProductoEnFactura]] = None

class FacturaUpdate(BaseModel):
    cantidad_total: Optional[float] = None
    cantidad_adicional: Optional[float] = None
    IVA: Optional[float] = None
    observaciones: Optional[str] = None

class ProductoFactura(BaseModel):
    id: int
    nombre: str
    precio_unitario: float
    cantidad: int

class FacturaDB(FacturaBase):
    numero_factura: int
    productos: Optional[List[ProductoFactura]] = []


class FacturaConIncidencia(FacturaDB):
    incidencia_nombre: Optional[str] = None

    class Config:
        orm_mode = True
