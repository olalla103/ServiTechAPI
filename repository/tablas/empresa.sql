CREATE TABLE Empresas (
    cif VARCHAR(9) PRIMARY KEY NOT NULL,
    nombre_fiscal VARCHAR(150 NOT NULL),
    calle_y_numero VARCHAR(200) NOT NULL,
    codigo_postal INT NOT NULL,
    ciudad VARCHAR(150) NOT NULL,
    provincia VARCHAR(150) NOT NULL,
    correo_electronico VARCHAR(150) NOT NULL
);

ALTER TABLE Empresas
    MODIFY COLUMN cif VARCHAR(9) NOT NULL,
    MODIFY COLUMN nombre_fiscal VARCHAR(150) NOT NULL,
    MODIFY COLUMN calle_y_numero VARCHAR(200) NOT NULL,
    MODIFY COLUMN codigo_postal INT NOT NULL,
    MODIFY COLUMN ciudad VARCHAR(150) NOT NULL,
    MODIFY COLUMN provincia VARCHAR(150) NOT NULL,
    MODIFY COLUMN correo_electronico VARCHAR(150) NOT NULL;