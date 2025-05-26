from fastapi import APIRouter, HTTPException, Query
from typing import List, Any
from models.incidencias import IncidenciaDB, IncidenciaUpdate, PausaIncidencia
from repository.handler_incidencia import (
    get_all_incidencias,
    get_incidencia_by_id,
    get_all_incidencias_pendientes,
    get_all_incidencias_resueltas,
    get_incidencia_by_tecnico_id,
    get_incidencia_by_cliente_id,
    get_incidencias_en_curso, update_incidencia, insertar_incidencia, filtrar_incidencias_handler, pausar_incidencia,
    reanudar_incidencia
)

router = APIRouter()

@router.get("/", response_model=List[IncidenciaDB])
def listar_incidencias():
    return get_all_incidencias()

from models.incidencias import IncidenciaCreate

@router.post("/", response_model=IncidenciaDB)
def crear_incidencia(datos: IncidenciaCreate):
    nueva_id = insertar_incidencia(datos.model_dump())
    if not nueva_id:
        raise HTTPException(status_code=400, detail="No se pudo crear la incidencia")
    return get_incidencia_by_id(nueva_id)


# 1. Ver todas las incidencias pendientes (máximo 5, ordenadas por fecha)
@router.get("/pendientes", response_model=List[IncidenciaDB])
def listar_incidencias_pendientes():
    return get_all_incidencias_pendientes()

# 2. Ver todas las incidencias resueltas (máximo 5, ordenadas por fecha final descendente)
@router.get("/resueltas", response_model=List[IncidenciaDB])
def listar_incidencias_resueltas():
    return get_all_incidencias_resueltas()

# 3. Ver todas las incidencias de un técnico por su ID
@router.get("/tecnico/{tecnico_id}", response_model=List[IncidenciaDB])
def listar_incidencias_por_tecnico(tecnico_id: int):
    return get_incidencia_by_tecnico_id(tecnico_id)

# 4. Ver todas las incidencias de un cliente por su ID
@router.get("/cliente/{cliente_id}", response_model=List[IncidenciaDB])
def listar_incidencias_por_cliente(cliente_id: int):
    return get_incidencia_by_cliente_id(cliente_id)

# 5. Ver todas las incidencias en curso (en_reparacion), info extendida
@router.get("/en-reparacion", response_model=List[Any])  # Puedes definir un modelo de respuesta custom si quieres
def listar_incidencias_en_curso():
    return get_incidencias_en_curso()

# 6. Obtener incidencia por ID (debe ir al final)
@router.get("/{incidencia_id}", response_model=IncidenciaDB)
def obtener_incidencia(incidencia_id: int):
    incidencia = get_incidencia_by_id(incidencia_id)
    if not incidencia:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    return incidencia


@router.put("/{incidencia_id}", response_model=IncidenciaDB)
def actualizar_incidencia(incidencia_id: int, datos: IncidenciaUpdate):
    incidencia_modificada = update_incidencia(incidencia_id, datos.dict(exclude_unset=True))
    if not incidencia_modificada:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada o no se pudo actualizar")
    return incidencia_modificada

@router.get("/filtro", response_model=List[IncidenciaDB])
def filtrar_incidencias(
    estado: str = Query(None),
    tipo: str = Query(None),
    tecnico_id: int = Query(None),
    cliente_id: int = Query(None)
):
    return filtrar_incidencias_handler(estado, tipo, tecnico_id, cliente_id)

@router.patch("/pausar/{incidencia_id}", response_model=IncidenciaDB)
def endpoint_pausar_incidencia(incidencia_id: int, datos: PausaIncidencia):
    incidencia_modificada = pausar_incidencia(incidencia_id, datos.fecha_hora_pausa)
    if not incidencia_modificada:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada o no se pudo pausar")
    return incidencia_modificada

@router.patch("/reanudar/{incidencia_id}", response_model=IncidenciaDB)
def endpoint_reanudar_incidencia(incidencia_id: int):
    incidencia_modificada = reanudar_incidencia(incidencia_id)
    if not incidencia_modificada:
        raise HTTPException(status_code=400, detail="No se pudo reanudar: revisa estado o si está pausada.")
    return incidencia_modificada

