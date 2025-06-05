from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import date, time, datetime

class IncidenciaBase(BaseModel):
    descripcion: str
    fecha_reporte: datetime        # Fecha y hora de reporte
    estado: Literal['pendiente', 'en_reparacion', 'resuelta']
    direccion: str
    fecha_inicio: Optional[datetime] = None    # Fecha y hora de inicio
    fecha_final: Optional[datetime] = None     # Fecha y hora de finalización
    horas: Optional[str] = None               # Tiempo total trabajado
    cliente_id: int
    tecnico_id: int
    tipo: Literal['presencial', 'remota']
    pausada: bool
    fecha_hora_pausa: Optional[datetime] = None  # Fecha y hora de la pausa
    fecha_ultimo_reinicio: Optional[datetime] = None  # <--- AÑADE ESTO

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

    @field_validator('horas', mode='before')
    def format_horas(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            parts = v.split(':')
            if len(parts) == 3:
                try:
                    h, m, s = [int(x) for x in parts]
                    return f"{h:02}:{m:02}:{s:02}"
                except Exception:
                    return v
            return v
        if hasattr(v, 'strftime'):
            return v.strftime('%H:%M:%S')
        return str(v)

    @field_validator('fecha_hora_pausa')
    def fecha_pausa_en_rango(cls, v, info):
        fecha_inicio = info.data.get('fecha_inicio')
        fecha_final = info.data.get('fecha_final')
        # Aseguramos tipos date
        if fecha_inicio and isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.date()
        if fecha_final and isinstance(fecha_final, datetime):
            fecha_final = fecha_final.date()
        if v and fecha_inicio and fecha_final:
            if not (fecha_inicio <= v.date() <= fecha_final):
                raise ValueError('La fecha/hora de pausa debe estar entre la fecha de inicio y la de finalización')
        return v

class IncidenciaCreate(IncidenciaBase):
    pass

class PausaIncidencia(BaseModel):
    fecha_hora_pausa: datetime

class FinalizarIncidenciaInput(BaseModel):
    fecha_final: str  # formato "2025-06-06 18:11:00"
    horas: str        # formato "01:32:21"

class IncidenciaUpdate(BaseModel):
    horas: Optional[str] = None
    estado: Optional[Literal['pendiente', 'en_reparacion', 'resuelta']] = None
    fecha_inicio: Optional[datetime] = None
    fecha_final: Optional[datetime] = None
    fecha_hora_pausa: Optional[datetime] = None
    # Puedes añadir más campos si los vas a actualizar desde el front

class IncidenciaDB(IncidenciaBase):
    id: int
    model_config = {"from_attributes": True}
