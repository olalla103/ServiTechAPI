import pymysql

from fecha_utils import timedelta, time
from models.incidencias import IncidenciaDB
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


########################### VER TODAS LA INCIDENCIAS ###########################
def _to_time_if_needed(val):
    if val is None or isinstance(val, time):
        return val
    if isinstance(val, timedelta):
        total_seconds = int(val.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return time(hours, minutes, seconds)
    # Si por algún motivo es string, intenta convertirlo
    if isinstance(val, str):
        h, m, s = map(int, val.split(":"))
        return time(h, m, s)
    # Si es otra cosa, devuélvelo tal cual (o pon None)
    return None

def get_all_incidencias():
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias"
            cursor.execute(sql)
            incidencias = cursor.fetchall()
            for incidencia in incidencias:
                incidencia["horas"] = _to_time_if_needed(incidencia.get("horas"))
            return [IncidenciaDB(**incidencia) for incidencia in incidencias]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencias: {e}")
        return []
    except Exception as ex:
        print(f"Error al convertir incidencia: {ex}")
        return []




########################### VER UNA INCIDENCIA POR ID DE INCIDENCIA ###########################
def get_incidencia_by_id(incidencia_id: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias WHERE id = %s"
            cursor.execute(sql, (incidencia_id,))
            incidencia = cursor.fetchone()
            if incidencia and "horas" in incidencia:
                incidencia["horas"] = _to_time_if_needed(incidencia["horas"])
            return IncidenciaDB(**incidencia) if incidencia else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencia por id: {e}")
        return None
    except Exception as ex:
        print(f"Error al convertir incidencia por id: {ex}")
        return None



########################### VER TODAS LAS INCIDENCIAS PENDIENTES ###########################
def get_all_incidencias_pendientes():
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias where estado = 'pendiente' order by fecha_reporte asc limit 5"
            cursor.execute(sql)
            incidencias = cursor.fetchall()
            return [IncidenciaDB(**incidencia) for incidencia in incidencias]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencias: {e}")
        return []
    except Exception as ex:
        print(f"Error al convertir incidencia: {ex}")
        return []


########################### VER TODAS LAS INCIDENCIAS RESUELTAS ###########################
def get_all_incidencias_resueltas():
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias where estado = 'resuelta' order by fecha_final desc limit 5"
            cursor.execute(sql)
            incidencias = cursor.fetchall()
            for incidencia in incidencias:
                incidencia["horas"] = _to_time_if_needed(incidencia.get("horas"))
            return [IncidenciaDB(**incidencia) for incidencia in incidencias]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencias: {e}")
        return []
    except Exception as ex:
        print(f"Error al convertir incidencia: {ex}")
        return []

########################### VER TODAS LAS INCIDENCIAS POR ID DE TÉCNICO ###########################
def get_incidencia_by_tecnico_id(tecnico_id: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias WHERE tecnico_id = %s"
            cursor.execute(sql, (tecnico_id,))
            incidencia = cursor.fetchall()
            for inc in incidencia:
                inc["horas"] = _to_time_if_needed(inc.get("horas"))  # CORREGIDO AQUÍ
            return [IncidenciaDB(**inc) for inc in incidencia] if incidencia else []
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencia por tecnico id: {e}")
        return []
    except Exception as ex:
        print(f"Error al convertir incidencia: {ex}")
        return []


########################### VER TODAS LAS INCIDENCIAS POR ID DE CLIENTE ###########################
def get_incidencia_by_cliente_id(cliente_id: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias WHERE cliente_id = %s"
            cursor.execute(sql, (cliente_id,))
            incidencia = cursor.fetchall()
            for inc in incidencia:
                inc["horas"] = _to_time_if_needed(inc.get("horas"))
            return [IncidenciaDB(**inc) for inc in incidencia] if incidencia else []
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencia por cliente id: {e}")
        return []
    except Exception as ex:
        print(f"Error al convertir incidencia: {ex}")
        return []

########################### VER TODAS LAS INCIDENCIAS EN REPARACIÓN ###########################
def get_incidencias_en_curso():
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT
                    i.id,
                    i.descripcion,
                    i.tipo,
                    i.fecha_inicio,
                    i.horas,
                    i.pausada,
                    u_cliente.nombre AS nombre_cliente,
                    u_cliente.apellido1 AS apellido1_cliente,
                    u_tecnico.nombre AS nombre_tecnico,
                    u_tecnico.apellido1 AS apellido1_tecnico
                FROM incidencias i
                JOIN usuarios u_tecnico ON i.tecnico_id = u_tecnico.id
                JOIN usuarios u_cliente ON i.cliente_id = u_cliente.id
                WHERE i.estado = 'en_reparacion'
                ORDER BY i.fecha_inicio ASC, i.horas ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencias en curso: {e}")
        return []

########################### ACTUALIZAR INCIDENCIA ###########################
def update_incidencia(incidencia_id: int, datos: dict):
    """
    Actualiza los campos permitidos (horas y estado) de una incidencia.
    `datos` debe ser un dict con claves 'horas' y/o 'estado'
    """
    campos = []
    valores = []

    if "horas" in datos:
        # Si el valor es de tipo time, conviértelo a string para SQL (HH:MM:SS)
        horas_val = datos["horas"]
        if isinstance(horas_val, time):
            horas_val = horas_val.strftime("%H:%M:%S")
        elif isinstance(horas_val, timedelta):
            # Convierte timedelta a string HH:MM:SS
            total_seconds = int(horas_val.total_seconds())
            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60
            horas_val = f"{h:02}:{m:02}:{s:02}"
        campos.append("horas = %s")
        valores.append(horas_val)

    if "estado" in datos:
        campos.append("estado = %s")
        valores.append(datos["estado"])

    if not campos:
        return None  # Nada que actualizar

    valores.append(incidencia_id)

    sql = f"UPDATE incidencias SET {', '.join(campos)} WHERE id = %s"

    try:
        with get_cursor() as cursor:
            cursor.execute(sql, tuple(valores))
            if cursor.rowcount == 0:
                return None
        # Devuelve la incidencia actualizada
        return get_incidencia_by_id(incidencia_id)
    except Exception as e:
        print(f"Error al actualizar incidencia: {e}")
        return None

############################ PAUSAR INCIDENCIA ###########################
def pausar_incidencia(incidencia_id: int, fecha_hora_pausa):
    try:
        incidencia = get_incidencia_by_id(incidencia_id)
        if not incidencia:
            print("Incidencia no encontrada.")
            return None
        if incidencia.estado != 'en_reparacion':
            print("Solo se puede pausar una incidencia en reparación.")
            return None
        if incidencia.pausada:
            print("La incidencia ya está pausada.")
            return None

        with get_cursor() as cursor:
            sql = "UPDATE incidencias SET pausada = TRUE, fecha_hora_pausa = %s WHERE id = %s"
            if fecha_hora_pausa is not None and hasattr(fecha_hora_pausa, "strftime"):
                fecha_hora_pausa = fecha_hora_pausa.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(sql, (fecha_hora_pausa, incidencia_id))
            if cursor.rowcount == 0:
                return None
        return get_incidencia_by_id(incidencia_id)
    except Exception as e:
        print(f"Error al pausar incidencia: {e}")
        return None

############################ REANUDAR INCIDENCIA ###########################

def reanudar_incidencia(incidencia_id: int):
    try:
        incidencia = get_incidencia_by_id(incidencia_id)
        if not incidencia:
            print("Incidencia no encontrada.")
            return None
        if incidencia.estado != 'en_reparacion':
            print("Solo se puede reanudar una incidencia en reparación.")
            return None
        if not incidencia.pausada:
            print("La incidencia no está pausada.")
            return None

        with get_cursor() as cursor:
            sql = "UPDATE incidencias SET pausada = FALSE, fecha_hora_pausa = NULL WHERE id = %s"
            cursor.execute(sql, (incidencia_id,))
            if cursor.rowcount == 0:
                return None
        return get_incidencia_by_id(incidencia_id)
    except Exception as e:
        print(f"Error al reanudar incidencia: {e}")
        return None


############################ FILTROS ###########################
def filtrar_incidencias_handler(estado, tipo, tecnico_id, cliente_id):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias WHERE 1=1"
            valores = []
            if estado:
                sql += " AND estado = %s"
                valores.append(estado)
            if tipo:
                sql += " AND tipo = %s"
                valores.append(tipo)
            if tecnico_id:
                sql += " AND tecnico_id = %s"
                valores.append(tecnico_id)
            if cliente_id:
                sql += " AND cliente_id = %s"
                valores.append(cliente_id)
            cursor.execute(sql, tuple(valores))
            incidencias = cursor.fetchall()
            for incidencia in incidencias:
                incidencia["horas"] = _to_time_if_needed(incidencia.get("horas"))
            return [IncidenciaDB(**incidencia) for incidencia in incidencias]
    except Exception as e:
        print(f"Error al filtrar incidencias: {e}")
        return []
