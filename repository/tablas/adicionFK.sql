ALTER TABLE Empresas ADD FOREIGN KEY (admin_id) REFERENCES Usuarios(id);
ALTER TABLE Incidencias ADD FOREIGN KEY (cliente_id) REFERENCES Usuarios(id);
ALTER TABLE Incidencias ADD FOREIGN KEY (tecnico_id) REFERENCES Usuarios(id);
ALTER TABLE Facturas ADD FOREIGN KEY (tecnico_id) REFERENCES Usuarios(id);
ALTER TABLE Facturas ADD FOREIGN KEY (cliente_id) REFERENCES Usuarios(id);
ALTER TABLE Facturas ADD FOREIGN KEY (incidencia_id) REFERENCES Incidencias(id);