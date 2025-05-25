from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import date, time

class IncidenciaBase(BaseModel):
    descripcion: str
    fecha_reporte: date
    estado: Literal['pendiente', 'en_reparacion', 'resuelta']
    direccion: str
    fecha_inicio: Optional[date] = None
    fecha_final: Optional[date] = None
    horas: Optional[time] = None
    cliente_id: int
    tecnico_id: int

    @field_validator('cliente_id', 'tecnico_id')
    def ids_positivos(cls, v):
        if v <= 0:
            raise ValueError('Los IDs de cliente y técnico deben ser positivos')
        return v

    @field_validator('fecha_final')
    def fecha_final_no_anterior(cls, v, info):
        fecha_inicio = info.data.get('fecha_inicio')
        if v and fecha_inicio and v < fecha_inicio:
            raise ValueError('La fecha final no puede ser anterior a la fecha de inicio')
        return v

    @field_validator('horas')
    def horas_no_negativas(cls, v):
        # 'time' no puede ser negativa, pero puedes asegurar que no sea '00:00:00' si lo deseas
        if v is not None and v.hour == 0 and v.minute == 0 and v.second == 0:
            raise ValueError('Las horas deben ser mayores que cero')
        return v

class IncidenciaCreate(IncidenciaBase):
    pass

class IncidenciaDB(IncidenciaBase):
    id: int

    class Config:
        orm_mode = True
