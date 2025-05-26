import pymysql

from models.empresas import EmpresaDB
from repository.conexion import get_cursor

def insertar_empresa(empresa):
    """
    empresa: dict con las claves según la estructura de la tabla empresas
    """
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO empresas
                (cif, nombre_fiscal, calle_y_numero, codigo_postal, ciudad, provincia, correo_electronico)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                empresa["cif"],
                empresa["nombre_fiscal"],
                empresa["calle_y_numero"],
                empresa["codigo_postal"],
                empresa["ciudad"],
                empresa["provincia"],
                empresa["correo_electronico"]
            )
            cursor.execute(sql, valores)
            return empresa["cif"]  # El identificador es el CIF
    except pymysql.MySQLError as e:
        print(f"Error al insertar empresa: {e}")
        return None

def get_all_empresas():
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM empresas"
            cursor.execute(sql)
            empresas = cursor.fetchall()
            return [EmpresaDB(**empresa) for empresa in empresas]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar empresas: {e}")
        return []

def get_empresa_by_cif(cif: str):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM empresas WHERE cif = %s"
            cursor.execute(sql, (cif,))
            empresa = cursor.fetchone()
            return EmpresaDB(**empresa) if empresa else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar empresa por CIF: {e}")
        return None

def get_empresa_by_nombre(nombre_fiscal: str):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM empresas WHERE nombre_fiscal = %s"
            cursor.execute(sql, (nombre_fiscal,))
            empresa = cursor.fetchone()
            return EmpresaDB(**empresa) if empresa else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar empresa por nombre: {e}")
        return None

def actualizar_empresa(cif: str, campos: dict):
    if not campos:
        return False
    try:
        with get_cursor() as cursor:
            set_clause = ", ".join([f"{k} = %s" for k in campos])
            valores = list(campos.values()) + [cif]
            sql = f"UPDATE empresas SET {set_clause} WHERE cif = %s"
            cursor.execute(sql, valores)
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al actualizar empresa: {e}")
        return False

def eliminar_empresa(cif: str):
    try:
        with get_cursor() as cursor:
            sql = "DELETE FROM empresas WHERE cif = %s"
            cursor.execute(sql, (cif,))
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al eliminar empresa: {e}")
        return False

def get_empresas_by_ciudad(ciudad: str):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM empresas WHERE ciudad = %s"
            cursor.execute(sql, (ciudad,))
            empresas = cursor.fetchall()
            return [EmpresaDB(**empresa) for empresa in empresas]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar empresas por ciudad: {e}")
        return []

def get_empresas_by_provincia(provincia: str):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM empresas WHERE provincia = %s"
            cursor.execute(sql, (provincia,))
            empresas = cursor.fetchall()
            return [EmpresaDB(**empresa) for empresa in empresas]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar empresas por provincia: {e}")
        return []

