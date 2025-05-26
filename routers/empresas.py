from fastapi import APIRouter, HTTPException
from typing import List
from models.empresas import EmpresaDB, EmpresaCreate, EmpresaUpdate
from repository.handler_empresa import (
    get_all_empresas,
    get_empresa_by_cif,
    insertar_empresa,
    actualizar_empresa,
    eliminar_empresa,
    get_empresa_by_nombre, get_empresas_by_ciudad, get_empresas_by_provincia
)

router = APIRouter()

# ==========================
# === CONSULTAS (GET) ======
# ==========================

# Listar todas las empresas
@router.get("/", response_model=List[EmpresaDB])
def listar_empresas():
    return get_all_empresas()

# Obtener una empresa por CIF
@router.get("/{cif}", response_model=EmpresaDB)
def obtener_empresa(cif: str):
    empresa = get_empresa_by_cif(cif)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

# (Opcional) Buscar empresa por nombre fiscal
@router.get("/nombre/{nombre_fiscal}", response_model=EmpresaDB)
def buscar_empresa_por_nombre(nombre_fiscal: str):
    empresa = get_empresa_by_nombre(nombre_fiscal)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

# ==============================
# === CREACIÓN (POST) ==========
# ==============================

# Crear una nueva empresa
@router.post("/", response_model=EmpresaDB)
def crear_empresa(datos: EmpresaCreate):
    nueva_cif = insertar_empresa(datos.model_dump())
    if not nueva_cif:
        raise HTTPException(status_code=400, detail="No se pudo crear la empresa")
    return get_empresa_by_cif(nueva_cif)

# ==============================
# === EDICIÓN (PATCH) ==========
# ==============================

# Editar una empresa existente
@router.patch("/{cif}")
def editar_empresa(cif: str, datos: EmpresaUpdate):
    campos = datos.model_dump(exclude_unset=True)
    ok = actualizar_empresa(cif, campos)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la empresa")
    return {"ok": True}

# ==============================
# === ELIMINACIÓN (DELETE) =====
# ==============================

# Eliminar una empresa por CIF
@router.delete("/{cif}")
def borrar_empresa(cif: str):
    ok = eliminar_empresa(cif)
    if not ok:
        raise HTTPException(status_code=404, detail="No se pudo eliminar la empresa")
    return {"ok": True}

@router.get("/ciudad/{ciudad}", response_model=List[EmpresaDB])
def listar_empresas_por_ciudad(ciudad: str):
    return get_empresas_by_ciudad(ciudad)

@router.get("/provincia/{provincia}", response_model=List[EmpresaDB])
def listar_empresas_por_provincia(provincia: str):
    return get_empresas_by_provincia(provincia)


