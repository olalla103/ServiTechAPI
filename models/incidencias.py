from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import date, time, datetime

class IncidenciaBase(BaseModel):
    descripcion: str
    fecha_reporte: date
    estado: Literal['pendiente', 'en_reparacion', 'resuelta']
    direccion: str
    fecha_inicio: Optional[datetime] = None
    fecha_final: Optional[date] = None
    horas: Optional[time] = None
    cliente_id: int
    tecnico_id: int
    tipo: Literal['presencial', 'remota']
    pausada: bool
    fecha_hora_pausa: Optional[datetime] = None

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
        if v is not None and v.hour == 0 and v.minute == 0 and v.second == 0:
            raise ValueError('Las horas deben ser mayores que cero')
        return v

    @field_validator('fecha_hora_pausa')
    def fecha_pausa_en_rango(cls, v, info):
        fecha_inicio = info.data.get('fecha_inicio')
        fecha_final = info.data.get('fecha_final')
        if v and fecha_inicio and fecha_final:
            if not (fecha_inicio <= v.date() <= fecha_final):
                raise ValueError('La fecha/hora de pausa debe estar entre la fecha de inicio y la de finalización')
        return v

class IncidenciaCreate(IncidenciaBase):
    pass

class PausaIncidencia(BaseModel):
    fecha_hora_pausa: datetime

class IncidenciaUpdate(BaseModel):
    horas: Optional[time] = None
    estado: Optional[Literal['pendiente', 'en_reparacion', 'resuelta']] = None

class IncidenciaDB(IncidenciaBase):
    id: int

    class Config:
        orm_mode = True
