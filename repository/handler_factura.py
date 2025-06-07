from datetime import datetime

import pymysql
from models.facturas import FacturaDB, FacturaConIncidencia
from repository.conexion import get_cursor
from repository.handler_incidencia import get_incidencia_by_id
from repository.handler_producto import get_producto_by_id
from fpdf import FPDF


from datetime import datetime

def insertar_factura(factura):
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO facturas
                (fecha_emision, tiempo_total, cantidad_total, cantidad_adicional, IVA, observaciones,
                 tecnico_id, cliente_id, incidencia_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                factura["fecha_emision"],
                factura["tiempo_total"],
                factura["cantidad_total"],
                factura["cantidad_adicional"],
                factura["IVA"],
                factura.get("observaciones"),
                factura["tecnico_id"],
                factura["cliente_id"],
                factura["incidencia_id"]
            )
            cursor.execute(sql, valores)
            return cursor.lastrowid
    except pymysql.MySQLError as e:
        print(f"Error al insertar factura: {e}")
        return None

def insertar_factura_producto(factura_id, producto_id, cantidad):
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO facturaproducto (factura_id, producto_id, cantidad)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (factura_id, producto_id, cantidad))
    except Exception as e:
        print(f"Error al insertar producto en factura: {e}")

def crear_factura_backend(factura):
    # 1. Obtener la incidencia relacionada
    incidencia = get_incidencia_by_id(factura["incidencia_id"])
    if not incidencia:
        raise Exception("Incidencia no encontrada")

    # 2. Calcular tiempo_total (float de horas)
    def horas_to_float(horas_str):
        if not horas_str:
            return 0
        h, m, s = [int(x) for x in horas_str.split(":")]
        return h + m/60 + s/3600

    horas_str = incidencia.horas or "00:00:00"
    tiempo_total = round(horas_to_float(horas_str), 2)

    # 3. Calcular productos extra
    productos = factura.get("productos", [])
    cantidad_adicional = 0
    for prod in productos:
        producto_obj = get_producto_by_id(prod["producto_id"])
        precio_unitario = producto_obj.precio if producto_obj else 0
        cantidad_adicional += (precio_unitario * prod.get("cantidad", 1))
    cantidad_adicional = round(cantidad_adicional, 2)

    # 4. Calcular cantidad_total
    cantidad_total = round(tiempo_total * 20 + cantidad_adicional, 2)

    # 5. Calcular IVA
    iva = round(0.21 * cantidad_total, 2)

    # 6. Montar el diccionario para insertar
    factura_dict = {
        "fecha_emision": datetime.now(),
        "tiempo_total": tiempo_total,
        "cantidad_total": cantidad_total,
        "cantidad_adicional": cantidad_adicional,
        "IVA": iva,
        "observaciones": factura.get("observaciones", ""),
        "tecnico_id": factura["tecnico_id"],
        "cliente_id": factura["cliente_id"],
        "incidencia_id": factura["incidencia_id"],
    }

    print("DEBUG - factura_dict que se va a insertar:", factura_dict)

    # 7. Insertar la factura y obtener su id
    nueva_factura_id = insertar_factura(factura_dict)

    # 8. Insertar los productos asociados en facturaproducto
    for prod in productos:
        insertar_factura_producto(
            nueva_factura_id,
            prod["producto_id"],
            prod.get("cantidad", 1)
        )

    return nueva_factura_id

def get_all_facturas():
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT f.*, i.descripcion AS incidencia_nombre
                FROM facturas f
                LEFT JOIN incidencias i ON f.incidencia_id = i.id
            """
            cursor.execute(sql)
            facturas = cursor.fetchall()
            return [FacturaDB(**normaliza_factura(factura)) for factura in facturas]
    except Exception as e:
        print(f"Error al recuperar facturas: {e}")
        return []

def get_factura_por_incidencia_id(incidencia_id):
    with get_cursor() as cursor:
        sql = "SELECT * FROM facturas WHERE incidencia_id = %s LIMIT 1"
        cursor.execute(sql, (incidencia_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_facturas_por_incidencia(incidencia_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT f.*, i.descripcion AS incidencia_nombre
                FROM facturas f
                LEFT JOIN incidencias i ON f.incidencia_id = i.id
                WHERE f.incidencia_id = %s
            """
            cursor.execute(sql, (incidencia_id,))
            facturas = cursor.fetchall()
            return [FacturaConIncidencia(**factura) for factura in facturas]
    except Exception as e:
        print(f"Error al recuperar facturas por incidencia: {e}")
        return []


def calcular_cantidad_adicional(factura_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT SUM(fp.cantidad * p.precio) AS cantidad_adicional
                FROM facturaproducto fp
                JOIN productos p ON fp.producto_id = p.id
                WHERE fp.factura_id = %s
            """
            cursor.execute(sql, (factura_id,))
            row = cursor.fetchone()
            return row["cantidad_adicional"] if row and row["cantidad_adicional"] is not None else 0.0
    except Exception as e:
        print(f"Error al calcular cantidad adicional: {e}")
        return 0.0

def actualizar_cantidad_adicional_en_factura(factura_id: int):
    nueva_cantidad = calcular_cantidad_adicional(factura_id)
    try:
        with get_cursor() as cursor:
            sql = "UPDATE facturas SET cantidad_adicional = %s WHERE numero_factura = %s"
            cursor.execute(sql, (nueva_cantidad, factura_id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar cantidad adicional: {e}")
        return False

from datetime import datetime

from datetime import datetime

def normaliza_factura(factura):
    factura["fecha_emision"] = factura.get("fecha_emision") or datetime.now()
    factura["tiempo_total"] = factura.get("tiempo_total") or 0.0
    factura["cantidad_total"] = factura.get("cantidad_total") or 0.0
    factura["IVA"] = factura.get("IVA") or 21.0
    return factura


def get_facturas_resueltas_por_tecnico(tecnico_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT f.*, i.descripcion AS incidencia_nombre
                FROM facturas f
                JOIN incidencias i ON f.incidencia_id = i.id
                WHERE i.tecnico_id = %s AND i.estado = 'resuelta'
            """
            cursor.execute(sql, (tecnico_id,))
            facturas = cursor.fetchall()

            facturas_clean = []
            for factura in facturas:
                factura = normaliza_factura(factura)
                facturas_clean.append(FacturaConIncidencia(**factura))
            return facturas_clean

    except Exception as e:
        print(f"Error al recuperar facturas resueltas: {e}")
        return []




def get_facturas_por_tecnico(tecnico_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT f.*, i.descripcion AS incidencia_nombre
                FROM facturas f
                LEFT JOIN incidencias i ON f.incidencia_id = i.id
                WHERE f.tecnico_id = %s
            """
            cursor.execute(sql, (tecnico_id,))
            facturas = cursor.fetchall()
            return [FacturaConIncidencia(**factura) for factura in facturas]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar facturas: {e}")
        return []


def get_factura_by_id(numero_factura: int):
    try:
        with get_cursor() as cursor:
            # 1. Saca la factura principal
            sql_factura = "SELECT * FROM facturas WHERE numero_factura = %s"
            cursor.execute(sql_factura, (numero_factura,))
            factura = cursor.fetchone()
            if not factura:
                return None

            # 2. Saca los productos asociados (JOIN bonito)
            sql_productos = """
                SELECT 
                    p.id, 
                    p.nombre, 
                    p.precio AS precio_unitario, 
                    fp.cantidad
                FROM facturaproducto fp
                JOIN productos p ON fp.producto_id = p.id
                WHERE fp.factura_id = %s
            """
            cursor.execute(sql_productos, (numero_factura,))
            productos = cursor.fetchall()  # lista de dicts

            # 3. Añade los productos al dict de la factura
            factura["productos"] = productos

            # 4. Calcula y añade el precio adicional
            factura["cantidad_adicional"] = sum(
                (prod["precio_unitario"] or 0) * (prod["cantidad"] or 0) for prod in productos
            )

            # --- Asegúrate de que los campos NUNCA son None ---
            factura["fecha_emision"] = factura.get("fecha_emision") or datetime.now()
            factura["tiempo_total"] = factura.get("tiempo_total") or 0.0
            factura["cantidad_total"] = factura.get("cantidad_total") or 0.0
            factura["IVA"] = factura.get("IVA") or 21.0  # si quieres forzar siempre 21
            # Puedes añadir otros campos por defecto si es necesario

            # 5. Devuelve la factura como objeto Pydantic
            return FacturaDB(**factura)

    except Exception as e:
        print(f"Error al recuperar factura por id: {e}")
        return None

def get_factura_by_tecnico_and_incidencia(tecnico_id: int, incidencia_id: int):
    with get_cursor() as cursor:
        sql = "SELECT * FROM facturas WHERE tecnico_id = %s AND incidencia_id = %s"
        cursor.execute(sql, (tecnico_id, incidencia_id))
        return cursor.fetchone()

def actualizar_cantidad_adicional_en_factura(factura_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                UPDATE facturas SET cantidad_adicional = (
                    SELECT IFNULL(SUM(fp.cantidad * p.precio), 0)
                    FROM facturaproducto fp
                    JOIN productos p ON fp.producto_id = p.id
                    WHERE fp.factura_id = %s
                )
                WHERE numero_factura = %s
            """
            cursor.execute(sql, (factura_id, factura_id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar cantidad adicional: {e}")
        return False


def actualizar_factura(numero_factura: int, campos: dict):
    if not campos:
        return False
    try:
        with get_cursor() as cursor:
            set_clause = ", ".join([f"{k} = %s" for k in campos])
            valores = list(campos.values()) + [numero_factura]
            sql = f"UPDATE facturas SET {set_clause} WHERE numero_factura = %s"
            cursor.execute(sql, valores)
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al actualizar factura: {e}")
        return False

def eliminar_factura(numero_factura: int):
    try:
        with get_cursor() as cursor:
            sql = "DELETE FROM facturas WHERE numero_factura = %s"
            cursor.execute(sql, (numero_factura,))
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al eliminar factura: {e}")
        return False

def calcular_cantidad_adicional(factura_id: int):
    """
    Calcula la cantidad adicional de una factura sumando (cantidad * precio) de todos los productos usados en la factura.
    """
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT SUM(fp.cantidad * p.precio) AS cantidad_adicional
                FROM facturaproducto fp
                JOIN productos p ON fp.producto_id = p.id
                WHERE fp.factura_id = %s
            """
            cursor.execute(sql, (factura_id,))
            row = cursor.fetchone()
            return row["cantidad_adicional"] if row and row["cantidad_adicional"] is not None else 0.0
    except Exception as e:
        print(f"Error al calcular cantidad adicional: {e}")
        return 0.0

def actualizar_cantidad_adicional_en_factura(factura_id: int):
    nueva_cantidad = calcular_cantidad_adicional(factura_id)
    try:
        with get_cursor() as cursor:
            sql = "UPDATE facturas SET cantidad_adicional = %s WHERE numero_factura = %s"
            cursor.execute(sql, (nueva_cantidad, factura_id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar cantidad adicional: {e}")
        return False

from datetime import datetime

def generar_pdf_factura(factura: 'FacturaDB', cliente: 'UsuarioDB' = None, tecnico: 'UsuarioDB' = None, ruta_salida: str = None):
    from fpdf import FPDF
    print("Cliente:", cliente)
    print("Técnico:", tecnico)
    print("Factura:", factura)
    print("Productos:", factura.productos)

    pdf = FPDF()
    pdf.add_page()
    # Carga fuentes solo una vez
    pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
    pdf.add_font('DejaVu', 'I', 'fonts/DejaVuSans-Oblique.ttf', uni=True)
    pdf.add_font('DejaVu', 'BI', 'fonts/DejaVuSans-BoldOblique.ttf', uni=True)

    pdf.set_font('DejaVu', '', 13)
    pdf.set_text_color(0, 0, 0)  # SIEMPRE negro después del header de color

    # ... (resto del código igual que tu ejemplo) ...

    # Cabecera
    pdf.set_text_color(43, 158, 140)
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(0, 12, f"Factura #{getattr(factura, 'numero_factura', '-')}", ln=True, align='L')
    pdf.set_text_color(110, 110, 110)
    pdf.set_font('DejaVu', '', 12)
    fecha_raw = str(getattr(factura, 'fecha_emision', ''))
    try:
        fecha_dt = datetime.strptime(fecha_raw, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            fecha_dt = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S")
        except Exception:
            fecha_dt = getattr(factura, 'fecha_emision', datetime.now())
    fecha_str = fecha_dt.strftime("%d/%m/%Y")
    pdf.cell(0, 8, f"Fecha: {fecha_str}", ln=True, align='L')
    pdf.ln(2)

    # Cliente
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(45, 8, "Cliente:", ln=False)
    pdf.set_font("DejaVu", "", 13)
    if cliente:
        nombre_cliente = getattr(cliente, "nombre", None) or cliente.get("nombre", "-")
        apellido1_cliente = getattr(cliente, "apellido1", None) or cliente.get("apellido1", "-")
        nombre_cliente = f"{nombre_cliente} {apellido1_cliente}"
    else:
        nombre_cliente = f"ID: {getattr(factura, 'cliente_id', '-')}"
    pdf.cell(0, 8, nombre_cliente, ln=True)

    # Técnico
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(45, 8, "Técnico:", ln=False)
    pdf.set_font("DejaVu", "", 13)
    if tecnico:
        nombre_tecnico = getattr(tecnico, "nombre", None) or tecnico.get("nombre", "-")
        apellido1_tecnico = getattr(tecnico, "apellido1", None) or tecnico.get("apellido1", "-")
        nombre_tecnico = f"{nombre_tecnico} {apellido1_tecnico}"
    else:
        nombre_tecnico = f"ID: {getattr(factura, 'tecnico_id', '-')}"
    pdf.cell(0, 8, nombre_tecnico, ln=True)
    pdf.ln(3)

    # Tabla de productos
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(70, 8, "Producto", border=1)
    pdf.cell(30, 8, "Cantidad", border=1, align='C')
    pdf.cell(30, 8, "Precio", border=1, align='R')
    pdf.ln()
    pdf.set_font("DejaVu", "", 11)
    productos = getattr(factura, "productos", []) or []
    if not productos:
        pdf.cell(0, 8, "No hay productos en esta factura.", ln=True)
    else:
        for prod in productos:
            nombre = getattr(prod, "nombre", None) or prod.get("nombre", "-")
            cantidad = getattr(prod, "cantidad", None) or prod.get("cantidad", "-")
            precio_unitario = getattr(prod, "precio_unitario", None) or prod.get("precio_unitario", 0.0)
            pdf.cell(70, 8, str(nombre), border=1)
            pdf.cell(30, 8, str(cantidad), border=1, align='C')
            pdf.cell(30, 8, f"{precio_unitario:.2f} €", border=1, align='R')
            pdf.ln()
    pdf.ln(1)

    # Totales
    base = getattr(factura, "cantidad_total", 0.0)
    adicional = getattr(factura, "cantidad_adicional", 0.0)
    iva = getattr(factura, "IVA", 0.0)
    total = (base or 0.0) + (adicional or 0.0) + (iva or 0.0)

    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(70, 8, "Base", border=0)
    pdf.cell(30, 8, "", border=0)
    pdf.cell(30, 8, f"{base:.2f} €", border=0, align='R')
    pdf.ln()
    pdf.cell(70, 8, "Productos", border=0)
    pdf.cell(30, 8, "", border=0)
    pdf.cell(30, 8, f"{adicional:.2f} €", border=0, align='R')
    pdf.ln()
    pdf.cell(70, 8, "IVA", border=0)
    pdf.cell(30, 8, "", border=0)
    pdf.cell(30, 8, f"{iva:.2f} €", border=0, align='R')
    pdf.ln()
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(70, 10, "TOTAL", border=0)
    pdf.cell(30, 10, "", border=0)
    pdf.cell(30, 10, f"{total:.2f} €", border=0, align='R')
    pdf.ln(10)


    # Observaciones
    observaciones = getattr(factura, "observaciones", None)
    if observaciones:
        pdf.set_font("DejaVu", "I", 11)
        pdf.set_text_color(122, 122, 122)
        pdf.multi_cell(0, 8, f"Observaciones: {observaciones}")
        pdf.set_text_color(0, 0, 0)
    # Footer
    pdf.set_y(-30)
    pdf.set_font("DejaVu", "I", 13)
    pdf.set_text_color(188, 188, 188)
    pdf.cell(0, 10, "ServiTech · Factura generada automáticamente", 0, 0, 'C')

    if ruta_salida:
        pdf.output(ruta_salida)
    else:
        pdf.output(f"/ruta/a/factura{factura.numero_factura}.pdf")
    return pdf
