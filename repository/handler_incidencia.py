import pymysql

from fecha_utils import timedelta, time
from models.incidencias import IncidenciaDB
from repository.conexion import get_cursor

from datetime import datetime

def fix_datetime_field(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(val, str):
        # Si viene solo fecha
        if len(val) == 10:
            return val + " 00:00:00"
        # Si viene con T (ISO), cámbialo a espacio
        if "T" in val:
            val = val.replace("T", " ")
        # Si viene con punto y milisegundos, quítalo
        if "." in val:
            val = val.split(".")[0]
        # Ahora intenta parsear siempre y devolver string con formato SQL
        try:
            dt = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            # Si no se puede, devuelve tal cual (último recurso)
            return val
    return None

def _to_time_if_needed(val):
    if val is None or isinstance(val, time):
        return val
    if isinstance(val, timedelta):
        total_seconds = int(val.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return time(hours, minutes, seconds)
    if isinstance(val, str):
        h, m, s = map(int, val.split(":"))
        return time(h, m, s)
    return None


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
                fix_datetime_field(incidencia["fecha_reporte"]),
                incidencia["estado"],
                incidencia["direccion"],
                fix_datetime_field(incidencia.get("fecha_inicio")),
                fix_datetime_field(incidencia.get("fecha_final")),
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
                inc["horas"] = _to_time_if_needed(inc.get("horas"))
            return [IncidenciaDB(**inc) for inc in incidencia] if incidencia else []
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencia por tecnico id: {e}")
        return []
    except Exception as ex:
        print(f"Error al convertir incidencia: {ex}")
        return []

########################### VER TODAS LAS INCIDENCIAS POR ID DE TÉCNICO EN REPARACIÓN ###########################
def get_incidencia_by_tecnico_id_en_reparacion(tecnico_id: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias WHERE tecnico_id = %s and estado = 'en_reparacion'"
            cursor.execute(sql, (tecnico_id,))
            incidencia = cursor.fetchall()
            for inc in incidencia:
                inc["horas"] = _to_time_if_needed(inc.get("horas"))
            return [IncidenciaDB(**inc) for inc in incidencia] if incidencia else []
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencia por tecnico id: {e}")
        return []
    except Exception as ex:
        print(f"Error al convertir incidencia: {ex}")
        return []

########################### VER TODAS LAS INCIDENCIAS POR ID DE TÉCNICO PENDIENTES ###########################
def get_incidencia_by_tecnico_id_pendiente(tecnico_id: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias WHERE tecnico_id = %s and estado = 'pendiente'"
            cursor.execute(sql, (tecnico_id,))
            incidencia = cursor.fetchall()
            for inc in incidencia:
                inc["horas"] = _to_time_if_needed(inc.get("horas"))
            return [IncidenciaDB(**inc) for inc in incidencia] if incidencia else []
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencia por tecnico id: {e}")
        return []
    except Exception as ex:
        print(f"Error al convertir incidencia: {ex}")
        return []

########################### VER TODAS LAS INCIDENCIAS POR ID DE TÉCNICO RESUELTAS ###########################
def get_incidencia_by_tecnico_id_resuelta(tecnico_id: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM incidencias WHERE tecnico_id = %s and estado = 'resuelta'"
            cursor.execute(sql, (tecnico_id,))
            incidencia = cursor.fetchall()
            for inc in incidencia:
                inc["horas"] = _to_time_if_needed(inc.get("horas"))
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
                    *
                FROM incidencias
                WHERE estado = 'en_reparacion'
                ORDER BY fecha_inicio ASC, horas ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error al recuperar incidencias en curso: {e}")
        return []

########################### ACTUALIZAR INCIDENCIA ###########################
def update_incidencia(incidencia_id: int, datos: dict):
    print(f"Datos recibidos para update: {datos}")
    print(f"Intentando actualizar incidencia {incidencia_id} con datos: {datos}")
    """
    Actualiza los campos permitidos (horas, estado, fecha_inicio, fecha_final) de una incidencia.
    """
    campos = []
    valores = []

    if "horas" in datos:
        horas_val = datos["horas"]
        if isinstance(horas_val, time):
            horas_val = horas_val.strftime("%H:%M:%S")
        elif isinstance(horas_val, timedelta):
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

    if "fecha_inicio" in datos:
        campos.append("fecha_inicio = %s")
        valores.append(fix_datetime_field(datos["fecha_inicio"]))  # <-- adaptado

    if "fecha_final" in datos:
        campos.append("fecha_final = %s")
        valores.append(fix_datetime_field(datos["fecha_final"]))  # <-- adaptado

    # Si quieres añadir fecha_reporte también:
    if "fecha_reporte" in datos:
        campos.append("fecha_reporte = %s")
        valores.append(fix_datetime_field(datos["fecha_reporte"]))

    if not campos:
        return None  # Nada que actualizar

    valores.append(incidencia_id)
    sql = f"UPDATE incidencias SET {', '.join(campos)} WHERE id = %s"
    print(f"QUERY: {sql}")
    print(f"VALORES: {valores}")
    try:
        with get_cursor() as cursor:
            cursor.execute(sql, tuple(valores))
            if cursor.rowcount == 0:
                return None
        return get_incidencia_by_id(incidencia_id)
    except Exception as e:
        print(f"Error al actualizar incidencia: {e}")
        return None


    valores.append(incidencia_id)

    sql = f"UPDATE incidencias SET {', '.join(campos)} WHERE id = %s"

    try:
        with get_cursor() as cursor:
            cursor.execute(sql, tuple(valores))
            if cursor.rowcount == 0:
                return None
        return get_incidencia_by_id(incidencia_id)
    except Exception as e:
        print(f"Error al actualizar incidencia: {e}")
        return None

############################ PAUSAR INCIDENCIA ###########################


def update_incidencia_pausa(cursor, incidencia_id, fecha_hora_pausa_str, horas_str):
    sql = """
        UPDATE incidencias
        SET pausada = TRUE,
            fecha_hora_pausa = %s,
            horas = %s
        WHERE id = %s
    """
    cursor.execute(sql, (fecha_hora_pausa_str, horas_str, incidencia_id))
    return cursor.rowcount > 0


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

        # Calcula las horas acumuladas
        horas_str = calcular_horas_totales(incidencia, fecha_hora_pausa)
        # Normaliza fecha_hora_pausa
        if isinstance(fecha_hora_pausa, str) and "T" in fecha_hora_pausa:
            fecha_hora_pausa_str = fecha_hora_pausa.split(".")[0].replace("T", " ")
        elif isinstance(fecha_hora_pausa, datetime):
            fecha_hora_pausa_str = fecha_hora_pausa.strftime('%Y-%m-%d %H:%M:%S')
        else:
            fecha_hora_pausa_str = fecha_hora_pausa

        with get_cursor() as cursor:
            update_ok = update_incidencia_pausa(cursor, incidencia_id, fecha_hora_pausa_str, horas_str)
            if not update_ok:
                return None
        return get_incidencia_by_id(incidencia_id)

    except Exception as e:
        print(f"Error al pausar incidencia: {e}")
        return None


def calcular_horas_totales(incidencia, fecha_hora_pausa):
    # Convierte fechas a datetime si son string
    if isinstance(fecha_hora_pausa, str):
        if "T" in fecha_hora_pausa:
            fecha_hora_pausa_dt = datetime.strptime(fecha_hora_pausa.split(".")[0], "%Y-%m-%dT%H:%M:%S")
        else:
            fecha_hora_pausa_dt = datetime.strptime(fecha_hora_pausa, "%Y-%m-%d %H:%M:%S")
    else:
        fecha_hora_pausa_dt = fecha_hora_pausa

    fecha_inicio_dt = incidencia.fecha_inicio
    if isinstance(fecha_inicio_dt, str):
        fecha_inicio_dt = datetime.strptime(fecha_inicio_dt, "%Y-%m-%d %H:%M:%S")

    tiempo_transcurrido = fecha_hora_pausa_dt - fecha_inicio_dt

    # Suma el tiempo a las horas acumuladas
    horas_previas = incidencia.horas or time(0, 0, 0)
    if isinstance(horas_previas, str):
        h, m, s = map(int, horas_previas.split(":"))
        horas_previas = timedelta(hours=h, minutes=m, seconds=s)
    elif isinstance(horas_previas, time):
        horas_previas = timedelta(hours=horas_previas.hour, minutes=horas_previas.minute, seconds=horas_previas.second)
    else:
        horas_previas = timedelta()

    total_horas = horas_previas + tiempo_transcurrido

    # Convierte a formato HH:MM:SS para guardar en MySQL
    total_seconds = int(total_horas.total_seconds())
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    horas_str = f"{h:02}:{m:02}:{s:02}"
    return horas_str


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
            # Al reanudar, pausada = FALSE y fecha_hora_pausa = NULL
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
                # Transforma los campos datetime a string si hace falta
                if "fecha_reporte" in incidencia:
                    incidencia["fecha_reporte"] = fix_datetime_field(incidencia["fecha_reporte"])
                if "fecha_inicio" in incidencia:
                    incidencia["fecha_inicio"] = fix_datetime_field(incidencia["fecha_inicio"])
                if "fecha_final" in incidencia:
                    incidencia["fecha_final"] = fix_datetime_field(incidencia["fecha_final"])
                if "fecha_hora_pausa" in incidencia:
                    incidencia["fecha_hora_pausa"] = fix_datetime_field(incidencia["fecha_hora_pausa"])
            return [IncidenciaDB(**incidencia) for incidencia in incidencias]
    except Exception as e:
        print(f"Error al filtrar incidencias: {e}")
        return []

def finalizar_incidencia(incidencia_id: int, fecha_final: str, horas: str):
    """
    Marca la incidencia como resuelta, guarda fecha_final y horas trabajadas.
    - incidencia_id: id de la incidencia a finalizar.
    - fecha_final: string con formato "YYYY-MM-DD HH:MM:SS"
    - horas: string con formato "HH:MM:SS"
    """
    try:
        with get_cursor() as cursor:
            sql = """
                UPDATE incidencias
                SET estado = 'resuelta', fecha_final = %s, horas = %s
                WHERE id = %s
            """
            cursor.execute(sql, (fecha_final, horas, incidencia_id))
            if cursor.rowcount == 0:
                print("No se encontró la incidencia para finalizar.")
                return None
        # Devuelve la incidencia actualizada
        return get_incidencia_by_id(incidencia_id)
    except Exception as e:
        print(f"Error al finalizar incidencia: {e}")
        return None