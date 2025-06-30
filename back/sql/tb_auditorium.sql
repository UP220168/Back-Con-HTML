-- ============================================
-- TABLA DE AUDITORIOS - tb_auditorium (Simplificado)
-- ============================================

-- Creación de la tabla de auditorios
CREATE TABLE tb_auditorium (
    aud_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    aud_name VARCHAR(100) NOT NULL,
    aud_total_rows INT NOT NULL CHECK (aud_total_rows > 0),
    aud_seats_per_row INT NOT NULL CHECK (aud_seats_per_row > 0),
    aud_row_format ENUM('letters', 'numbers') DEFAULT 'letters',
    aud_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aud_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes en auditorios
CREATE INDEX idx_auditorium_name ON tb_auditorium(aud_name);

-- Trigger simple para actualizar timestamp
DELIMITER //
CREATE TRIGGER update_auditorium_timestamp
    BEFORE UPDATE ON tb_auditorium
    FOR EACH ROW
BEGIN
    -- Asegurar que el formato de fila sea 'letters' para nueva funcionalidad
    IF NEW.aud_row_format IS NULL THEN
        SET NEW.aud_row_format = 'letters';
    END IF;
    
    -- Actualizar timestamp
    SET NEW.aud_updated = CURRENT_TIMESTAMP;
END//

DELIMITER ;

INSERT INTO tb_auditorium (aud_id, aud_name, aud_total_rows, aud_seats_per_row, aud_row_format) VALUES
(UUID(), 'Sala 1', 10, 10, 'letters'),
(UUID(), 'Sala 2', 15, 10, 'letters'),
(UUID(), 'Sala VIP', 5, 10, 'letters');