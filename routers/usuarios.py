from fastapi import APIRouter, HTTPException
from typing import List
from models.usuarios import UsuarioDB
from repository.handler_usuario import get_all_usuarios, get_usuario_by_id

router = APIRouter()

@router.get("/", response_model=List[UsuarioDB])
def listar_usuarios():
    return get_all_usuarios()

@router.get("/{usuario_id}", response_model=UsuarioDB)
def obtener_usuario(usuario_id: int):
    usuario = get_usuario_by_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
