from fastapi import APIRouter, HTTPException
from typing import List
from models.producto import ProductoDB
from repository.handler_producto import get_all_productos, get_producto_by_id

router = APIRouter()

@router.get("/", response_model=List[ProductoDB])
def listar_productos():
    return get_all_productos()

@router.get("/{producto_id}", response_model=ProductoDB)
def obtener_producto(producto_id: int):
    producto = get_producto_by_id(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto
