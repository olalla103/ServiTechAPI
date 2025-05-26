from pydantic import BaseModel, field_validator
from typing import Optional
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

class FacturaCreate(FacturaBase):
    pass

class FacturaUpdate(BaseModel):
    fecha_emision: Optional[datetime] = None
    tiempo_total: Optional[float] = None
    cantidad_total: Optional[float] = None
    cantidad_adicional: Optional[float] = None
    IVA: Optional[float] = None
    observaciones: Optional[str] = None
    tecnico_id: Optional[int] = None
    cliente_id: Optional[int] = None
    incidencia_id: Optional[int] = None

class FacturaDB(FacturaBase):
    numero_factura: int

    class Config:
        orm_mode = True
