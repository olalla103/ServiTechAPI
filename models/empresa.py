# models/empresa.py
from pydantic import BaseModel, field_validator


class EmpresaBase(BaseModel):
   cif:str
   nombre_fiscal:str
   calle_y_numero:str
   codigo_postal:int
   ciudad:str
   provincia:str
   correo_electronico:str

  # Validación del código postal
   @field_validator('codigo_postal')
   def codigo_postal_valido(cls, v):
       if not (10000 <= v <= 99999):
           raise ValueError('El código postal debe tener 5 cifras y ser positivo')
       return v


class EmpresaCreate(EmpresaBase):
    pass

class EmpresaDB(EmpresaBase):
    class Config:
        orm_mode = True