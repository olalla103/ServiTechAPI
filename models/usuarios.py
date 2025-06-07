from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import date

from models.direcciones import DireccionBase


class UsuarioBase(BaseModel):
    nombre: str
    apellido1: str
    apellido2: str
    email: EmailStr
    contraseña: str
    telefono: str
    fecha_nacimiento: Optional[date] = None
    especialidad: Optional[str] = None
    numero_seguridad_social: Optional[str] = None
    admin_empresa: bool
    empresa_id: Optional[str] = None
    direcciones: List[DireccionBase] = []

    @field_validator('telefono')
    def telefono_valido(cls, v):
        if not (v.isdigit() and len(v) == 9):
            raise ValueError('El teléfono debe tener 9 cifras numéricas')
        return v

    @field_validator('nombre', 'apellido1', 'apellido2')
    def campos_no_vacios(cls, v, field):
        if not v or not v.strip():
            raise ValueError(f'El campo {field.name} no puede estar vacío')
        return v

    @field_validator('numero_seguridad_social')
    def nss_valido(cls, v):
        if v is not None and len(v) != 12:
            raise ValueError('El número de la seguridad social debe tener 12 cifras')
        return v

    @field_validator('contraseña')
    def contraseña_segura(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

    @field_validator('empresa_id')
    def empresa_id_valido(cls, v, info):
        admin = info.data.get('admin_empresa')
        if admin and (v is None or not v.strip()):
            raise ValueError('Un usuario administrador debe tener empresa_id')
        return v

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    email: Optional[str] = None
    contraseña: Optional[str] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    especialidad: Optional[str] = None
    numero_seguridad_social: Optional[str] = None
    admin_empresa: Optional[bool] = None
    empresa_id: Optional[str] = None
    direcciones: Optional[List[DireccionBase]] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CredencialesLogin(BaseModel):
    email: str
    contraseña: str

class UsuarioDB(UsuarioBase):
    pass


    class Config:
        orm_mode = True
