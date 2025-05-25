import pymysql
from models.incidencia import IncidenciaDB
from repository.conexion import get_cursor

def insertar_incidencia(incidencia):
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO incidencias
                (descripcion, fecha_reporte, estado, direccion, fecha_inicio, fecha_final, horas, cliente_id, tecnico_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                incidencia["descripcion"],
                incidencia["fecha_reporte"],
                incidencia["estado"],
                incidencia["direccion"],
                incidencia.get("fecha_inicio"),
                incidencia.get("fecha_final"),
                incidencia.get("horas"),
                incidencia["cliente_id"],
                incidencia["tecnico_id"]
            )
            cursor.execute(sql, valores)
            return cursor.lastrowid
    except pymysql.MySQLError as e:
        print(f"Error al insertar incidencia: {e}")
        return None

def get_all_incidencias():
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias"
            cursor.execute(sql)
            incidencias = cursor.fetchall()
            return [IncidenciaDB(**incidencia) for incidencia in incidencias]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencias: {e}")
        return []
    except Exception as ex:
        print(f"Error al convertir incidencia: {ex}")
        return []


def get_incidencia_by_id(incidencia_id: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias WHERE id = %s"
            cursor.execute(sql, (incidencia_id,))
            incidencia = cursor.fetchone()
            return IncidenciaDB(**incidencia) if incidencia else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencia por id: {e}")
        return None
