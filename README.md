# ServiTechAPI

API para la gestión de usuarios, productos, incidencias, direcciones, empresas y facturación en una empresa de servicios técnicos.

## Tecnologías
- Python 3.11+
- FastAPI
- Pydantic
- PyMySQL (MySQL/MariaDB)
- Uvicorn

---

## Endpoints principales

### 1. Usuarios (`/usuarios/`)
- Crear, listar, actualizar y eliminar usuarios.
- Consultar por nombre, apellidos, empresa, etc.

### 2. Productos (`/productos/`)
- CRUD de productos.
- Cada producto tiene nombre, descripción y precio.

### 3. Incidencias (`/incidencias/`)
- Crear y gestionar incidencias técnicas, asignar técnico, estado, tiempos, etc.

### 4. Direcciones (`/direcciones/`)
- CRUD de direcciones asociadas a usuarios.

### 5. Empresas (`/empresas/`)
- Crear, listar, actualizar y eliminar empresas.
- Buscar por CIF, nombre, ciudad, provincia, código postal.

### 6. Facturas (`/facturas/`)
- CRUD de facturas.
- Relación con técnico, cliente, incidencia.

### 7. Relación factura-producto (`/factura_producto/`)
- Añadir productos usados en una factura, indicar cantidad.
- Consultar, actualizar cantidad y eliminar productos de una factura.

---

## Cómo usar la API

### Arranque del servidor

```bash
uvicorn main:app --reload
