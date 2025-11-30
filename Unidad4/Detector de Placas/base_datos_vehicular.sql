-- =============================================
-- SCRIPT DE BASE DE DATOS: CONTROL VEHICULAR
-- =============================================

DROP TABLE IF EXISTS Vehiculos;
DROP TABLE IF EXISTS Propietarios;

-- TABLA PROPIETARIOS
CREATE TABLE Propietarios (
    id_propietario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100) UNIQUE
);

-- TABLA VEHICULOS
CREATE TABLE Vehiculos (
    placa VARCHAR(20) PRIMARY KEY,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    anio INT NOT NULL,
    id_propietario INT,
    CONSTRAINT fk_propietario
    FOREIGN KEY (id_propietario) 
    REFERENCES Propietarios(id_propietario)
    ON DELETE SET NULL 
    ON UPDATE CASCADE
);

-- DATOS: PROPIETARIOS
INSERT INTO Propietarios (nombre, telefono, correo) VALUES 
('Roberto Sánchez', '667-123-4567', 'roberto.sanchez@email.com'),
('Laura Fernández', '667-987-6543', 'laura.fer@webmail.com'),
('Miguel Ángel Torres', '667-555-8888', 'miguel.torres@corp.net'),
('Diana Ruiz', '667-444-1111', 'diana.ruiz@social.org');

-- DATOS: VEHICULOS
INSERT INTO Vehiculos (placa, marca, modelo, anio, id_propietario) VALUES 
('VSF-82-88', 'Chevrolet', 'Corsa', 2007, 1),
('ZJS-512-A', 'Toyota', 'Tacoma', 2001, 2),
('VLT-632-R', 'Toyota', 'Camry', 2006, 2),
('VTB-82-62', 'Dodge', 'Altitude', 2012, 3),
('VTB-82-63', 'Dodge', 'Journey', 2015, 3),
('VGN-264-D', 'Hyundai', 'Tucson', 2024, 4);
