-- ============================================
-- TABLA DE AUDITORIOS - tb_auditorium
-- ============================================

-- Creación de la tabla de auditorios
CREATE TABLE tb_auditorium (
    aud_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    aud_name VARCHAR(100) NOT NULL,
    aud_capacity INT NOT NULL CHECK (aud_capacity > 0),
    aud_total_rows INT NOT NULL CHECK (aud_total_rows > 0),
    aud_seats_per_row INT NOT NULL CHECK (aud_seats_per_row > 0),
    aud_row_format ENUM('letters', 'numbers') DEFAULT 'letters',
    aud_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aud_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes en auditorios
CREATE INDEX idx_auditorium_name ON tb_auditorium(aud_name);
CREATE INDEX idx_auditorium_capacity ON tb_auditorium(aud_capacity);


-- Trigger para validar capacidad vs filas y asientos
DELIMITER //
CREATE TRIGGER validate_auditorium_capacity
    BEFORE INSERT ON tb_auditorium
    FOR EACH ROW
BEGIN
    DECLARE calculated_capacity INT;
    SET calculated_capacity = NEW.aud_total_rows * NEW.aud_seats_per_row;
    
    -- Validar que la capacidad coincida con filas x asientos
    IF NEW.aud_capacity != calculated_capacity THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'La capacidad debe ser igual a total_rows * seats_per_row';
    END IF;
    
    -- Asegurar que el formato de fila sea 'letters' para nueva funcionalidad
    IF NEW.aud_row_format IS NULL THEN
        SET NEW.aud_row_format = 'letters';
    END IF;
END//

-- Trigger para validar capacidad en actualización
CREATE TRIGGER validate_auditorium_capacity_update
    BEFORE UPDATE ON tb_auditorium
    FOR EACH ROW
BEGIN
    DECLARE calculated_capacity INT;
    SET calculated_capacity = NEW.aud_total_rows * NEW.aud_seats_per_row;
    
    -- Validar que la capacidad coincida con filas x asientos
    IF NEW.aud_capacity != calculated_capacity THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'La capacidad debe ser igual a total_rows * seats_per_row';
    END IF;
    
    -- Actualizar timestamp
    SET NEW.aud_updated = CURRENT_TIMESTAMP;
END//

DELIMITER ;

INSERT INTO tb_auditorium (aud_id, aud_name, aud_capacity, aud_total_rows, aud_seats_per_row, aud_row_format) VALUES
(UUID(), 'Sala 1', 100, 10, 10, 'letters'),
(UUID(), 'Sala 2', 150, 15, 10, 'letters'),
(UUID(), 'Sala VIP', 50, 5, 10, 'letters');