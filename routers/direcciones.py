from fastapi import APIRouter, HTTPException
from typing import List
from models.direcciones import DireccionCreate, DireccionDB, DireccionUpdate
from repository.handler_direcciones import (
    get_direcciones_usuario,
    get_direccion_by_id,
    insertar_direccion,
    actualizar_direccion,
    eliminar_direccion,
)

router = APIRouter()

# Listar direcciones de un usuario
@router.get("/usuarios/{usuario_id}/direcciones", response_model=List[DireccionDB])
def listar_direcciones_usuario(usuario_id: int):
    return get_direcciones_usuario(usuario_id)

# Crear una nueva dirección para un usuario
@router.post("/usuarios/{usuario_id}/direcciones", response_model=DireccionDB)
def crear_direccion_usuario(usuario_id: int, datos: DireccionCreate):
    nueva_id = insertar_direccion({**datos.model_dump(), "usuario_id": usuario_id})
    if not nueva_id:
        raise HTTPException(status_code=400, detail="No se pudo crear la dirección")
    direccion = get_direccion_by_id(nueva_id)
    return direccion

# Obtener una dirección por id
@router.get("/direcciones/{direccion_id}", response_model=DireccionDB)
def obtener_direccion(direccion_id: int):
    direccion = get_direccion_by_id(direccion_id)
    if not direccion:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return direccion

# Actualizar una dirección por id
@router.patch("/direcciones/{direccion_id}")
def editar_direccion(direccion_id: int, datos: DireccionUpdate):
    campos = datos.model_dump(exclude_unset=True)
    ok = actualizar_direccion(direccion_id, campos)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la dirección")
    return {"ok": True}

# Eliminar una dirección por id
@router.delete("/direcciones/{direccion_id}")
def borrar_direccion(direccion_id: int):
    ok = eliminar_direccion(direccion_id)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo eliminar la dirección")
    return {"ok": True}

