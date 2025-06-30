-- ============================================
-- TABLA DE TICKETS/BOLETOS - tb_ticket
-- ============================================

-- Creación de la tabla de tickets
CREATE TABLE tb_ticket (
    tic_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    tic_row VARCHAR(2) NOT NULL CHECK (tic_row REGEXP '^[A-Z]{1,2}$'), -- Soporte para A-Z, AA-ZZ
    tic_seat INT NOT NULL CHECK (tic_seat > 0),
    tic_scr_id CHAR(36) NOT NULL,
    tic_status ENUM('available', 'reserved', 'sold') DEFAULT 'available',
    tic_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tic_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tic_scr_id) REFERENCES tb_screening(scr_id) ON DELETE CASCADE,
    -- Un asiento por función (evitar duplicados)
    UNIQUE KEY unique_seat_per_screening (tic_scr_id, tic_row, tic_seat)
);

-- Índices para búsquedas frecuentes en tickets
CREATE INDEX idx_ticket_screening ON tb_ticket(tic_scr_id);
CREATE INDEX idx_ticket_status ON tb_ticket(tic_status);
CREATE INDEX idx_ticket_row_seat ON tb_ticket(tic_row, tic_seat);
CREATE INDEX idx_ticket_screening_status ON tb_ticket(tic_scr_id, tic_status);

-- Trigger para validar posición del asiento antes de insertar
DELIMITER //
CREATE TRIGGER validate_ticket_seat_insert
    BEFORE INSERT ON tb_ticket
    FOR EACH ROW
BEGIN
    DECLARE max_rows INT DEFAULT 0;
    DECLARE max_seats_per_row INT DEFAULT 0;
    DECLARE row_format ENUM('letters', 'numbers') DEFAULT 'letters';
    DECLARE current_row INT DEFAULT 0;
    
    -- Obtener configuración del auditorio
    SELECT a.aud_total_rows, a.aud_seats_per_row, a.aud_row_format
    INTO max_rows, max_seats_per_row, row_format
    FROM tb_auditorium a
    JOIN tb_screening s ON a.aud_id = s.scr_aud_id
    WHERE s.scr_id = NEW.tic_scr_id;
    
    -- Validar formato de fila según configuración del auditorio
    IF row_format = 'letters' THEN
        -- Convertir letra a número para validación (A=1, B=2, etc.)
        IF LENGTH(NEW.tic_row) = 1 THEN
            SET current_row = ASCII(NEW.tic_row) - 64; -- A=1, B=2, etc.
        ELSEIF LENGTH(NEW.tic_row) = 2 THEN
            SET current_row = (ASCII(LEFT(NEW.tic_row, 1)) - 64) * 26 + (ASCII(RIGHT(NEW.tic_row, 1)) - 64);
        ELSE
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Formato de fila inválido. Use A-Z o AA-ZZ';
        END IF;
        
        -- Validar que esté en formato de letras
        IF NEW.tic_row NOT REGEXP '^[A-Z]{1,2}$' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fila debe estar en formato de letras (A-Z)';
        END IF;
    ELSE
        -- Para formato numérico (compatibilidad futura)
        SET current_row = CAST(NEW.tic_row AS UNSIGNED);
    END IF;
    
    -- Validar que la fila esté dentro del rango
    IF current_row > max_rows THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fila especificada excede la capacidad del auditorio';
    END IF;
    
    -- Validar que el asiento esté dentro del rango
    IF NEW.tic_seat > max_seats_per_row THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El asiento especificado excede la capacidad de la fila';
    END IF;
END//

-- Trigger para validar cambios de estado de ticket
CREATE TRIGGER validate_ticket_status_update
    BEFORE UPDATE ON tb_ticket
    FOR EACH ROW
BEGIN
    DECLARE screening_status ENUM('scheduled', 'ongoing', 'finished', 'cancelled') DEFAULT 'scheduled';
    
    -- Obtener estado de la proyección
    SELECT scr_status INTO screening_status
    FROM tb_screening 
    WHERE scr_id = NEW.tic_scr_id;
    
    -- No permitir cambios si la función ya terminó o fue cancelada
    IF screening_status IN ('finished', 'cancelled') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se pueden modificar tickets de funciones terminadas o canceladas';
    END IF;
    
    -- No permitir volver a disponible un ticket vendido
    IF OLD.tic_status = 'sold' AND NEW.tic_status = 'available' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede liberar un ticket vendido directamente';
    END IF;
    
    -- Actualizar timestamp
    SET NEW.tic_updated = CURRENT_TIMESTAMP;
END//

-- Trigger para actualizar asientos disponibles cuando cambia el estado del ticket
CREATE TRIGGER update_available_seats_on_ticket_change
    AFTER UPDATE ON tb_ticket
    FOR EACH ROW
BEGIN
    DECLARE seat_change INT DEFAULT 0;
    
    -- Calcular cambio en asientos disponibles
    IF OLD.tic_status = 'available' AND NEW.tic_status IN ('reserved', 'sold') THEN
        SET seat_change = -1;
    ELSEIF OLD.tic_status IN ('reserved', 'sold') AND NEW.tic_status = 'available' THEN
        SET seat_change = 1;
    END IF;
    
    -- Actualizar contador de asientos disponibles
    IF seat_change != 0 THEN
        UPDATE tb_screening 
        SET scr_available_seats = scr_available_seats + seat_change
        WHERE scr_id = NEW.tic_scr_id;
    END IF;
END//

DELIMITER ;
