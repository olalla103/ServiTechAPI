from fastapi import APIRouter, HTTPException
from typing import List
from models.empresa import EmpresaDB
from repository.handler_empresa import get_all_empresas, get_empresa_by_cif

router = APIRouter()

@router.get("/", response_model=List[EmpresaDB])
def listar_empresas():
    return get_all_empresas()

@router.get("/{cif}", response_model=EmpresaDB)
def obtener_empresa(cif: str):
    empresa = get_empresa_by_cif(cif)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa
