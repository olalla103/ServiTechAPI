import pymysql
import traceback
from fecha_utils import timedelta, time
from models.incidencias import IncidenciaDB
from repository.conexion import get_cursor

from datetime import datetime, timezone


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
    if val is None:
        return None
    if isinstance(val, str):
        return val  # Ya string, lo devuelve tal cual
    if isinstance(val, time):
        return val.strftime('%H:%M:%S')
    if isinstance(val, timedelta):
        total_seconds = int(val.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return str(val)

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
                incidencia.get("horas") or "00:00:00",  # Asegura que horas sea un string "HH:MM:SS"
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
            sql = "SELECT * FROM incidencias where estado = 'pendiente' order by fecha_reporte asc "
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
        if isinstance(horas_val, str):
            # Ya está en el formato correcto
            pass
        elif isinstance(horas_val, time):
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
    print("VALOR HORAS AL UPDATE: ",horas_val,type(horas_val))
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

from datetime import datetime, timedelta
from models.incidencias import IncidenciaDB
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

        # LOGS: Valores actuales
        print(f"[PAUSAR] horas antes de la suma: {incidencia.horas} (type={type(incidencia.horas)})")
        print(f"[PAUSAR] fecha_inicio: {incidencia.fecha_inicio}")
        print(f"[PAUSAR] fecha_ultimo_reinicio: {incidencia.fecha_ultimo_reinicio}")
        print(f"[PAUSAR] fecha_hora_pausa recibida: {fecha_hora_pausa}")

        # Calcular tiempo transcurrido
        fecha_base = incidencia.fecha_ultimo_reinicio if incidencia.fecha_ultimo_reinicio else incidencia.fecha_inicio

        # Normalizar fechas
        if isinstance(fecha_base, str):
            fecha_base = datetime.strptime(fecha_base.split(".")[0].replace("T", " "), "%Y-%m-%d %H:%M:%S")
        if isinstance(fecha_hora_pausa, str):
            try:
                fecha_hora_pausa = datetime.fromisoformat(fecha_hora_pausa.replace("Z", "+00:00"))
            except Exception:
                fecha_hora_pausa = datetime.strptime(fecha_hora_pausa.split(".")[0].replace("T", " "), "%Y-%m-%d %H:%M:%S")

        # Eliminar zona horaria si existe
        if hasattr(fecha_base, 'tzinfo') and fecha_base.tzinfo is not None:
            fecha_base = fecha_base.astimezone(timezone.utc).replace(tzinfo=None)
        if hasattr(fecha_hora_pausa, 'tzinfo') and fecha_hora_pausa.tzinfo is not None:
            fecha_hora_pausa = fecha_hora_pausa.astimezone(timezone.utc).replace(tzinfo=None)

        tiempo_transcurrido = fecha_hora_pausa - fecha_base
        print(f"[PAUSAR] Tiempo transcurrido en este tramo: {tiempo_transcurrido}")

        # Obtener horas previas (siempre inicializar como timedelta(0))
        horas_previas = timedelta(0)
        if hasattr(incidencia, 'horas') and incidencia.horas is not None:
            try:
                if isinstance(incidencia.horas, time):
                    horas_previas = timedelta(
                        hours=incidencia.horas.hour,
                        minutes=incidencia.horas.minute,
                        seconds=incidencia.horas.second
                    )
                elif isinstance(incidencia.horas, str):
                    if ":" in incidencia.horas:
                        h, m, s = map(int, incidencia.horas.split(":"))
                        horas_previas = timedelta(hours=h, minutes=m, seconds=s)
                elif isinstance(incidencia.horas, timedelta):
                    horas_previas = incidencia.horas
                else:
                    print(f"Tipo no reconocido: {type(incidencia.horas)}")
            except Exception as e:
                print(f"Error al convertir horas: {e}")
                horas_previas = timedelta(0)

        print(f"[PAUSAR] Horas previas después de conversión: {horas_previas}")

        # Calcular total de horas y evitar negativos
        total_horas = horas_previas + tiempo_transcurrido
        if total_horas.total_seconds() < 0:
            print("[PAUSAR] El total de horas es negativo, se deja en 0.")
            total_horas = timedelta(0)
        total_seconds = int(total_horas.total_seconds())
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        horas_str = f"{h:02}:{m:02}:{s:02}"

        print(f"[PAUSAR] Guardando horas_str: {horas_str}")

        # Actualizar BD
        with get_cursor() as cursor:
            sql = """
                UPDATE incidencias
                SET pausada = TRUE,
                    fecha_hora_pausa = %s,
                    horas = %s,
                    fecha_ultimo_reinicio = NULL
                WHERE id = %s
            """
            cursor.execute(sql, (
                fecha_hora_pausa.strftime('%Y-%m-%d %H:%M:%S'),
                horas_str,
                incidencia_id
            ))
            if cursor.rowcount == 0:
                print("[PAUSAR] No se actualizó ninguna fila")
                return None

        return get_incidencia_by_id(incidencia_id)

    except Exception as e:
        print(f"Error al pausar incidencia: {e}")
        print(f"Traceback completo: {traceback.format_exc()}")
        return None


def calcular_horas_totales(incidencia, fecha_hora_pausa):
    if not incidencia or not fecha_hora_pausa:
        print("Faltan datos requeridos")
        return "00:00:00"
    # --- Convertir fecha_hora_pausa a datetime ---
    if isinstance(fecha_hora_pausa, str):
        try:
            fecha_hora_pausa_dt = datetime.fromisoformat(fecha_hora_pausa.replace("Z", "+00:00"))
        except Exception:
            if "T" in fecha_hora_pausa:
                fecha_hora_pausa_dt = datetime.strptime(fecha_hora_pausa.split(".")[0], "%Y-%m-%dT%H:%M:%S")
            else:
                fecha_hora_pausa_dt = datetime.strptime(fecha_hora_pausa, "%Y-%m-%d %H:%M:%S")
    else:
        fecha_hora_pausa_dt = fecha_hora_pausa

    # --- Convertir fecha_inicio a datetime ---
    fecha_inicio_dt = incidencia.fecha_inicio
    if isinstance(fecha_inicio_dt, str):
        try:
            fecha_inicio_dt = datetime.fromisoformat(fecha_inicio_dt.replace("Z", "+00:00"))
        except Exception:
            fecha_inicio_dt = datetime.strptime(fecha_inicio_dt, "%Y-%m-%d %H:%M:%S")

    # --- Siempre restar aware-naive ---
    if hasattr(fecha_inicio_dt, 'tzinfo') and fecha_inicio_dt.tzinfo is not None:
        fecha_inicio_dt = fecha_inicio_dt.replace(tzinfo=None)
    if hasattr(fecha_hora_pausa_dt, 'tzinfo') and fecha_hora_pausa_dt.tzinfo is not None:
        fecha_hora_pausa_dt = fecha_hora_pausa_dt.replace(tzinfo=None)

    # --- Calcular horas previas ---
    horas_previas = getattr(incidencia, "horas", None)
    if horas_previas is None:
        horas_previas = timedelta(0)
    elif isinstance(horas_previas, str):
        try:
            h, m, s = map(int, horas_previas.split(":"))
            horas_previas = timedelta(hours=h, minutes=m, seconds=s)
        except Exception:
            horas_previas = timedelta(0)
    elif isinstance(horas_previas, time):
        horas_previas = timedelta(hours=horas_previas.hour, minutes=horas_previas.minute, seconds=horas_previas.second)
    elif isinstance(horas_previas, timedelta):
        pass
    else:
        horas_previas = timedelta(0)

    # --- Calcular el nuevo tramo ---
    tiempo_tramo = fecha_hora_pausa_dt - fecha_inicio_dt
    if tiempo_tramo.total_seconds() < 0:
        tiempo_tramo = timedelta(0)  # Nunca sumar negativo

    # --- Sumamos ambos ---
    total_horas = horas_previas + tiempo_tramo

    # --- Guardar siempre como string "HH:MM:SS" ---
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

        now = datetime.now(timezone.utc)

        with get_cursor() as cursor:
            sql = """
                UPDATE incidencias
                SET pausada = FALSE,
                    fecha_hora_pausa = NULL,
                    fecha_ultimo_reinicio = %s
                WHERE id = %s
            """
            cursor.execute(sql, (now.strftime('%Y-%m-%d %H:%M:%S'), incidencia_id))
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