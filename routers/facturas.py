from fastapi import APIRouter, HTTPException
from typing import List
from models.factura import FacturaDB
from repository.handler_factura import get_all_facturas, get_factura_by_id

router = APIRouter()

@router.get("/", response_model=List[FacturaDB])
def listar_facturas():
    return get_all_facturas()

@router.get("/{numero_factura}", response_model=FacturaDB)
def obtener_factura(numero_factura: int):
    factura = get_factura_by_id(numero_factura)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura
