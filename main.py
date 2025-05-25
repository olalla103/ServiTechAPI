from fastapi import FastAPI
from routers import usuarios, empresas, productos, incidencias, facturas, factura_producto

app = FastAPI()
app.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
app.include_router(empresas.router, prefix="/empresas", tags=["empresas"])
app.include_router(productos.router, prefix="/productos", tags=["productos"])
app.include_router(incidencias.router, prefix="/incidencias", tags=["incidencias"])
app.include_router(facturas.router, prefix="/facturas", tags=["facturas"])
app.include_router(factura_producto.router, prefix="/factura-producto", tags=["factura-producto"])
