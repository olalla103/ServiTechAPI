--Empresa
    -- Empresas
INSERT INTO Empresas
    (cif, nombre_fiscal, calle_y_numero, codigo_postal, ciudad, provincia, correo_electronico)
VALUES
    ('A12345678', 'Servicios Integrales SL', 'Calle Falsa 123', 28080, 'Madrid', 'Madrid', 'info@servicios.com'),
    ('B23456789', 'Reparaciones Exprés SA', 'Avenida Siempre Viva 742', 46000, 'Valencia', 'Valencia', 'contacto@repexp.es'),
    ('23456789B', 'Juan Pérez Rodríguez', 'Calle del Autónomo 7', 41005, 'Sevilla', 'Sevilla', 'juanperez@autonomo.com');
;

--Usuarios
INSERT INTO Usuarios
    (nombre, apellido1, apellido2, telefono, fecha_nacimiento, especialidad, numero_seguridad_social, admin_empresa, empresa_id)
VALUES
    ('Ana', 'López', 'Martínez', '600123456', '1985-04-12', NULL, NULL, TRUE, 'A12345678'),
    ('Juan', 'Pérez', 'Rodríguez', '600234567', '1990-08-22', 'Fontanero', '234567890123', TRUE, '23456789B'),
    ('Luis', 'García', 'Fernández', '600345678', '1982-01-15', 'Técnico', '345678901234', FALSE, 'A12345678'),
    ('María', 'Núñez', 'Pereira', '600455679', '1992-05-15', NULL, NULL, FALSE, 'B23456789');
;

-- Algunos productos de ejemplo
INSERT INTO Productos (nombre, descripcion_tecnica) VALUES
('Bombilla LED', 'Bombilla LED 12W, E27'),
('Tubo PVC', 'Tubo PVC 2 metros'),
('Interruptor doble', 'Interruptor doble blanco'),
('Llave inglesa', 'Llave inglesa 250mm');


-- Incidencia: cliente María solicita reparación, atendida por Juan (autónomo)
INSERT INTO Incidencias
(descripcion, fecha_reporte, estado, direccion, fecha_inicio, fecha_final, horas, cliente_id, tecnico_id)
VALUES
('Reparación de fuga en lavabo', '2024-05-01', 'resuelta', 'Calle del Cliente 5', '2025-05-01', '2025-05-01', '01:00:00', 1, 2);

-- Incidencia: cliente de empresa atendido por técnico de empresa
INSERT INTO Incidencias
(descripcion, fecha_reporte, estado, direccion, fecha_inicio, fecha_final, horas, cliente_id, tecnico_id)
VALUES
('Corte de luz en oficina', '2024-05-02', 'en_reparacion', 'Avda. Empresa 123', '2025-03-28', '2025-03-28', '03:00:00', 4, 3);

-- Factura por incidencia resuelta por Juan el autónomo (id técnico = 2, cliente = 1, incidencia = 1)
INSERT INTO Facturas
(fecha_emision, tiempo_total, cantidad_total, cantidad_adicional, IVA, observaciones, tecnico_id, cliente_id, incidencia_id)
VALUES
('2024-05-03 10:00:00', 1.0, 100.00, 15.00, 21.00, 'Incluye materiales y desplazamiento', 2, 1, 1);

-- Factura por incidencia atendida por técnico de empresa (id técnico = 3, cliente = 4, incidencia = 2)
INSERT INTO Facturas
(fecha_emision, tiempo_total, cantidad_total, cantidad_adicional, IVA, observaciones, tecnico_id, cliente_id, incidencia_id)
VALUES
('2024-05-04 12:00:00', 2.0, 200.00, 0.00, 21.00, 'Reparación urgente', 3, 4, 2);

-- Relación productos/factura
INSERT INTO FacturaProducto (factura_id, producto_id) VALUES
(1, 1), -- Factura 1 usó Bombilla LED
(1, 2), -- Factura 1 usó Tubo PVC
(2, 3); -- Factura 2 usó Interruptor doble
