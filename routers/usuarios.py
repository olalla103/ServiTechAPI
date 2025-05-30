from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.usuarios import UsuarioDB, UsuarioCreate, UsuarioUpdate, TokenResponse
from repository.handler_incidencia import get_incidencia_by_tecnico_id_en_reparacion, \
    get_incidencia_by_tecnico_id_pendiente, get_incidencia_by_tecnico_id_resuelta
from repository.handler_usuario import (
    get_all_usuarios,
    get_usuario_by_id,
    insertar_usuario,
    get_usuario_by_nombre_apellidos,
    recuperar_emails,
    recuperar_telefonos,
    recuperar_especialidad,
    eliminar_usuario,
    get_usuarios_ordenados_por_columna,
    actualizar_usuario,
    get_usuario_by_email, get_clientes_by_empresa_id, get_cliente_by_id,
)
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "SUPERSECRETO_CAMBIALO123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 semana

router = APIRouter()

# --- CONSULTAS Y BÚSQUEDAS ---

# Buscar usuario por nombre y apellidos
@router.get("/buscar", response_model=UsuarioDB)
def buscar_usuario(nombre: str, apellido1: str, apellido2: str):
    usuario = get_usuario_by_nombre_apellidos(nombre, apellido1, apellido2)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.get("/clientes/empresa/{empresa_id}", response_model=List[dict])
def clientes_empresa(empresa_id: str):
    """
    Devuelve todos los clientes de una empresa según el criterio explicado.
    """
    return get_clientes_by_empresa_id(empresa_id)

@router.get("/clientes/{cliente_id}", response_model=dict)
def cliente_detalle(cliente_id: int):
    cliente = get_cliente_by_id(cliente_id)
    if cliente:
        return cliente
    else:
        return {}

# Obtener usuario por id
@router.get("/{usuario_id}", response_model=UsuarioDB)
def obtener_usuario(usuario_id: int):
    usuario = get_usuario_by_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.get("/clientes/{cliente_id}", response_model=dict)
def cliente_detalle(cliente_id: int):
    cliente = get_cliente_by_id(cliente_id)
    if cliente:
        return cliente
    else:
        return {}

# Obtener todos los usuarios
@router.get("/", response_model=List[UsuarioDB])
def listar_usuarios():
    return get_all_usuarios()

# Obtener usuarios ordenados por columna
@router.get("/ordenados", response_model=List[UsuarioDB])
def listar_usuarios_ordenados(
    columna: str = "nombre",
    ascendente: bool = True,
    skip: int = 0,
    limit: int = 100
):
    return get_usuarios_ordenados_por_columna(
        columna=columna,
        ascendente=ascendente,
        skip=skip,
        limit=limit
    )

# Recuperar emails de todos los usuarios
@router.get("/emails", response_model=List[str])
def endpoint_recuperar_emails():
    return recuperar_emails()

# Recuperar teléfonos de todos los usuarios
@router.get("/telefonos", response_model=List[str])
def endpoint_recuperar_telefonos():
    return recuperar_telefonos()

# Recuperar especialidad de un usuario
@router.get("/{usuario_id}/especialidad", response_model=Optional[str])
def endpoint_recuperar_especialidad(usuario_id: int):
    return recuperar_especialidad(usuario_id)


# --- CREACIÓN, EDICIÓN Y VERIFICACIÓN ---

# Insertar un usuario
@router.post("", response_model=UsuarioDB)
@router.post("/", response_model=UsuarioDB)
def crear_usuario(datos: UsuarioCreate):
    nueva_id = insertar_usuario(datos.model_dump())
    if not nueva_id:
        raise HTTPException(status_code=400, detail="No se pudo crear el usuario")
    return get_usuario_by_id(nueva_id)

# Cambiar teléfono del usuario
@router.patch("/{usuario_id}")
def actualizar_usuario_endpoint(usuario_id: int, datos: UsuarioUpdate):
    campos = datos.model_dump(exclude_unset=True)
    ok = actualizar_usuario(usuario_id, campos)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el usuario")
    return {"ok": True}


# Clave secreta fuerte (pon algo largo y seguro en producción)
SECRET_KEY = "SUPERSECRETO_CAMBIALO123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 semana

# Modelos de login
class LoginRequest(BaseModel):
    email: str
    contraseña: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def verificar_usuario_y_contraseña(email, contraseña):
    print("Llamando a get_usuario_by_email con:", email)
    usuario = get_usuario_by_email(email)
    print("Resultado usuario:", usuario)
    if not usuario:
        print("Usuario no encontrado")
        return False
    print("Contraseña en BBDD:", usuario.contraseña)
    if usuario.contraseña != contraseña:
        print("Contraseña incorrecta")
        return False
    print("Login correcto")
    return usuario



# Función para crear el token
def crear_token_acceso(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/verificar")
def endpoint_verificar_credenciales(datos: LoginRequest):
    usuario = verificar_usuario_y_contraseña(datos.email, datos.contraseña)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = crear_token_acceso({"sub": usuario.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": usuario
    }



# --- ELIMINACIÓN ---

# Eliminar usuario
@router.delete("/{usuario_id}", response_model=UsuarioDB)
def eliminar_usuario_endpoint(usuario_id: int):
    usuario = get_usuario_by_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    ok = eliminar_usuario(usuario_id)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo eliminar el usuario")
    return usuario  # Devuelves el usuario eliminado (antes de borrarlo)


