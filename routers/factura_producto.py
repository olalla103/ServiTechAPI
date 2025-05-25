from fastapi import APIRouter, HTTPException
from typing import List
from models.factura_producto import FacturaProductoDB
from repository.handler_factura_producto import get_all_factura_producto, get_factura_producto_by_ids

router = APIRouter()

@router.get("/", response_model=List[FacturaProductoDB])
def listar_factura_producto():
    return get_all_factura_producto()

@router.get("/{factura_id}/{producto_id}", response_model=FacturaProductoDB)
def obtener_factura_producto(factura_id: int, producto_id: int):
    relacion = get_factura_producto_by_ids(factura_id, producto_id)
    if not relacion:
        raise HTTPException(status_code=404, detail="Factura-producto no encontrada")
    return relacion
