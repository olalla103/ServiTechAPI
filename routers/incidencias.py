from fastapi import APIRouter, HTTPException
from typing import List
from models.incidencia import IncidenciaDB
from repository.handler_incidencia import get_all_incidencias, get_incidencia_by_id

router = APIRouter()

@router.get("/", response_model=List[IncidenciaDB])
def listar_incidencias():
    return get_all_incidencias()

@router.get("/{incidencia_id}", response_model=IncidenciaDB)
def obtener_incidencia(incidencia_id: int):
    incidencia = get_incidencia_by_id(incidencia_id)
    if not incidencia:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    return incidencia
