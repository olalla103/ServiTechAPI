CREATE TABLE Incidencias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    descripcion TEXT NOT NULL,
    fecha_reporte DATE NOT NULL,
    estado ENUM('pendiente', 'en_reparacion', 'resuelta'),
    direccion VARCHAR(254) NOT NULL,
    fecha_inicio DATE,
    fecha_final DATE,
    horas TIME,
    cliente_id INT,
    tecnico_id INT
);

ALTER TABLE Incidencias
    MODIFY COLUMN descripcion TEXT NOT NULL,
    MODIFY COLUMN fecha_reporte DATE NOT NULL,
    MODIFY COLUMN estado ENUM('pendiente', 'en_reparacion', 'resuelta') NOT NULL,
    MODIFY COLUMN direccion VARCHAR(254) NOT NULL,
    MODIFY COLUMN cliente_id INT NOT NULL,
    MODIFY COLUMN tecnico_id INT NOT NULL;