CREATE TABLE Facturas (
    numero_factura INT PRIMARY KEY AUTO_INCREMENT,
    fecha_emision DATETIME,
    tiempo_total FLOAT,
    cantidad_total FLOAT,
    cantidad_adicional FLOAT,
    IVA DECIMAL(5,2),
    observaciones TEXT,
    tecnico_id INT,
    cliente_id INT,
    incidencia_id INT
);