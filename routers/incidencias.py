from fastapi import APIRouter, HTTPException, Query
from typing import Any, List

from models.incidencias import (
    FinalizarIncidenciaInput,
    IncidenciaCreate,
    IncidenciaDB,
    IncidenciaUpdate,
    PausaIncidencia,
)
from repository.handler_incidencia import (
    filtrar_incidencias_handler,
    finalizar_incidencia,
    get_all_incidencias,
    get_all_incidencias_pendientes,
    get_all_incidencias_resueltas,
    get_incidencia_by_cliente_id,
    get_incidencia_by_id,
    get_incidencia_by_tecnico_id,
    get_incidencia_by_tecnico_id_en_reparacion,
    get_incidencia_by_tecnico_id_pendiente,
    get_incidencia_by_tecnico_id_resuelta,
    get_incidencias_en_curso,
    insertar_incidencia,
    pausar_incidencia,
    reanudar_incidencia,
    update_incidencia,
)

router = APIRouter()

# ----------------- GET endpoints -----------------

@router.get("/", response_model=List[IncidenciaDB])
def listar_incidencias():
    return get_all_incidencias()

@router.get("/pendientes", response_model=List[IncidenciaDB])
def listar_incidencias_pendientes():
    return get_all_incidencias_pendientes()

@router.get("/resueltas", response_model=List[IncidenciaDB])
def listar_incidencias_resueltas():
    return get_all_incidencias_resueltas()

@router.get("/tecnico/{tecnico_id}", response_model=List[IncidenciaDB])
def listar_incidencias_por_tecnico(tecnico_id: int):
    return get_incidencia_by_tecnico_id(tecnico_id)

@router.get("/tecnico/{tecnico_id}/en-reparacion", response_model=List[IncidenciaDB])
def incidencias_en_reparacion(tecnico_id: int):
    incidencias = get_incidencia_by_tecnico_id_en_reparacion(tecnico_id)
    return incidencias

@router.get("/tecnico/{tecnico_id}/pendientes", response_model=List[IncidenciaDB])
def incidencias_pendientes(tecnico_id: int):
    incidencias = get_incidencia_by_tecnico_id_pendiente(tecnico_id)
    return incidencias

@router.get("/tecnico/{tecnico_id}/resueltas", response_model=List[IncidenciaDB])
def incidencias_resueltas(tecnico_id: int):
    incidencias = get_incidencia_by_tecnico_id_resuelta(tecnico_id)
    return incidencias

@router.get("/cliente/{cliente_id}", response_model=List[IncidenciaDB])
def listar_incidencias_por_cliente(cliente_id: int):
    return get_incidencia_by_cliente_id(cliente_id)

@router.get("/en-reparacion", response_model=List[Any])  # Puedes definir un modelo de respuesta custom si quieres
def listar_incidencias_en_curso():
    return get_incidencias_en_curso()

@router.get("/filtro", response_model=List[IncidenciaDB])
def filtrar_incidencias(
    estado: str = Query(None),
    tipo: str = Query(None),
    tecnico_id: int = Query(None),
    cliente_id: int = Query(None),
):
    return filtrar_incidencias_handler(estado, tipo, tecnico_id, cliente_id)

@router.get("/{incidencia_id}", response_model=IncidenciaDB)
def obtener_incidencia(incidencia_id: int):
    incidencia = get_incidencia_by_id(incidencia_id)
    if not incidencia:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    return incidencia

# ----------------- POST endpoints -----------------

@router.post("/", response_model=IncidenciaDB)
def crear_incidencia(datos: IncidenciaCreate):
    nueva_id = insertar_incidencia(datos.model_dump())
    if not nueva_id:
        raise HTTPException(status_code=400, detail="No se pudo crear la incidencia")
    return get_incidencia_by_id(nueva_id)

# ----------------- PUT endpoints -----------------

@router.put("/{incidencia_id}", response_model=IncidenciaDB)
def actualizar_incidencia(incidencia_id: int, datos: IncidenciaUpdate):
    print(f"Datos recibidos para actualizar incidencia {incidencia_id}: {datos}")
    incidencia_modificada = update_incidencia(incidencia_id, datos.dict(exclude_unset=True))
    if not incidencia_modificada:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada o no se pudo actualizar")
    return incidencia_modificada

# ----------------- PATCH endpoints -----------------

import logging

@router.patch("/pausar/{incidencia_id}", response_model=IncidenciaDB)
def endpoint_pausar_incidencia(incidencia_id: int, datos: PausaIncidencia):
    import logging
    logging.warning(f"Recibido: {datos.fecha_hora_pausa}")
    if datos.fecha_hora_pausa is None:
        raise HTTPException(status_code=400, detail="Debe enviar la fecha y hora de la pausa.")
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

@router.patch("/finalizar/{incidencia_id}", response_model=IncidenciaDB)
def endpoint_finalizar_incidencia(incidencia_id: int, datos: FinalizarIncidenciaInput):
    incidencia_modificada = finalizar_incidencia(
        incidencia_id,
        datos.fecha_final,
        datos.horas
    )
    if not incidencia_modificada:
        raise HTTPException(status_code=400, detail="No se pudo finalizar la incidencia.")
    return incidencia_modificada
