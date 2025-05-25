CREATE TABLE Usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    apellido1 VARCHAR(60)NOT NULL,
    apellido2 VARCHAR(60) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    contraseña VARCHAR(128) NOT NULL,
    telefono VARCHAR(9) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    especialidad VARCHAR(60),
    numero_seguridad_social VARCHAR(12),
    admin_empresa BOOLEAN NOT NULL,
    empresa_id varchar(9) NOT NULL,
);


ALTER TABLE Usuarios
    MODIFY COLUMN empresa_id VARCHAR(9) NOT NULL,
    MODIFY COLUMN nombre VARCHAR(50) NOT NULL,
    MODIFY COLUMN apellido1 VARCHAR(60) NOT NULL,
    MODIFY COLUMN apellido2 VARCHAR(60) NOT NULL,
    MODIFY COLUMN telefono VARCHAR(9) NOT NULL,
    MODIFY COLUMN fecha_nacimiento DATE NOT NULL,
    MODIFY COLUMN admin_empresa BOOLEAN NOT NULL,
    MODIFY COLUMN empresa_id VARCHAR(9) NOT NULL;