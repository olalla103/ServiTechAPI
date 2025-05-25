CREATE TABLE FacturaProducto (
    factura_id INT,
    producto_id INT,
    PRIMARY KEY (factura_id, producto_id),
    FOREIGN KEY (factura_id) REFERENCES Facturas(numero_factura),
    FOREIGN KEY (producto_id) REFERENCES Productos(id)
);
