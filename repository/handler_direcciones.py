from models.direcciones import DireccionDB
from repository.conexion import get_cursor

# ==========================================
# Obtener todas las direcciones de un usuario
# ==========================================
def get_direcciones_usuario(usuario_id: int):
    """
    Devuelve una lista de todas las direcciones asociadas a un usuario.
    """
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM direcciones WHERE usuario_id = %s"
            cursor.execute(sql, (usuario_id,))
            direcciones = cursor.fetchall()
            # Construye objetos DireccionDB para cada registro
            return [DireccionDB(**d) for d in direcciones]
    except Exception as e:
        print(f"Error al recuperar direcciones: {e}")
        return []

# ==========================================
# Obtener una dirección por su ID
# ==========================================
def get_direccion_by_id(direccion_id: int):
    """
    Devuelve una dirección a partir de su ID.
    """
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM direcciones WHERE id = %s"
            cursor.execute(sql, (direccion_id,))
            direccion = cursor.fetchone()
            # Si existe la dirección, la devuelve como DireccionDB, si no devuelve None
            return DireccionDB(**direccion) if direccion else None
    except Exception as e:
        print(f"Error al recuperar dirección: {e}")
        return None

# ==========================================
# Insertar una nueva dirección
# ==========================================
def insertar_direccion(direccion: dict):
    """
    Inserta una nueva dirección en la base de datos.
    Devuelve el ID de la nueva dirección o None si hay error.
    """
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO direcciones
                (usuario_id, calle, numero, piso, puerta, ciudad, cp, provincia, pais)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                direccion["usuario_id"],
                direccion["calle"],
                direccion["numero"],
                direccion.get("piso"),
                direccion.get("puerta"),
                direccion["ciudad"],
                direccion["cp"],
                direccion["provincia"],
                direccion["pais"]
            )
            cursor.execute(sql, valores)
            return cursor.lastrowid
    except Exception as e:
        print(f"Error al insertar dirección: {e}")
        return None

# ==========================================
# Actualizar una dirección existente
# ==========================================
def actualizar_direccion(direccion_id: int, campos: dict):
    """
    Actualiza los campos indicados de una dirección.
    'campos' es un diccionario con los campos a modificar.
    Devuelve True si se actualizó, False si no.
    """
    if not campos:
        return False
    try:
        with get_cursor() as cursor:
            # Construye la parte SET de la consulta SQL dinámicamente
            set_clause = ", ".join([f"{k} = %s" for k in campos])
            valores = list(campos.values()) + [direccion_id]
            sql = f"UPDATE direcciones SET {set_clause} WHERE id = %s"
            cursor.execute(sql, valores)
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar dirección: {e}")
        return False

# ==========================================
# Eliminar una dirección por su ID
# ==========================================
def eliminar_direccion(direccion_id: int):
    """
    Elimina la dirección indicada por su ID.
    Devuelve True si se eliminó, False si hubo error.
    """
    try:
        with get_cursor() as cursor:
            sql = "DELETE FROM direcciones WHERE id = %s"
            cursor.execute(sql, (direccion_id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al eliminar dirección: {e}")
        return False
