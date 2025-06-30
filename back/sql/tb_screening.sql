-- ============================================
-- TABLA DE PROYECCIONES/FUNCIONES - tb_screening
-- ============================================

-- Creación de la tabla de proyecciones
CREATE TABLE tb_screening (
    scr_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    scr_mov_id CHAR(36) NOT NULL,
    scr_aud_id CHAR(36) NOT NULL,
    scr_date DATE NOT NULL,
    scr_time TIME NOT NULL,
    scr_price DECIMAL(10,2) NOT NULL CHECK (scr_price > 0),
    scr_available_seats INT NOT NULL DEFAULT 0,
    scr_status ENUM('scheduled', 'ongoing', 'finished', 'cancelled') DEFAULT 'scheduled',
    scr_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scr_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (scr_mov_id) REFERENCES tb_movie(mov_id) ON DELETE CASCADE,
    FOREIGN KEY (scr_aud_id) REFERENCES tb_auditorium(aud_id) ON DELETE CASCADE,
    -- Evitar proyecciones duplicadas en el mismo auditorio al mismo tiempo
    UNIQUE KEY unique_screening (scr_aud_id, scr_date, scr_time)
);

-- Índices para búsquedas frecuentes en proyecciones
CREATE INDEX idx_screening_date ON tb_screening(scr_date);
CREATE INDEX idx_screening_movie ON tb_screening(scr_mov_id);
CREATE INDEX idx_screening_auditorium ON tb_screening(scr_aud_id);
CREATE INDEX idx_screening_status ON tb_screening(scr_status);
CREATE INDEX idx_screening_datetime ON tb_screening(scr_date, scr_time);
CREATE INDEX idx_screening_available_seats ON tb_screening(scr_available_seats);

-- Trigger para inicializar asientos disponibles al crear proyección
DELIMITER //
CREATE TRIGGER initialize_screening_seats
    AFTER INSERT ON tb_screening
    FOR EACH ROW
BEGIN
    DECLARE auditorium_capacity INT DEFAULT 0;
    DECLARE total_rows INT DEFAULT 0;
    DECLARE seats_per_row INT DEFAULT 0;
    DECLARE row_format ENUM('letters', 'numbers') DEFAULT 'letters';
    DECLARE i INT DEFAULT 1;
    DECLARE j INT DEFAULT 1;
    DECLARE current_row_letter VARCHAR(2) DEFAULT '';
    
    -- Obtener configuración del auditorio
    SELECT aud_total_rows, aud_seats_per_row, aud_row_format
    INTO total_rows, seats_per_row, row_format
    FROM tb_auditorium 
    WHERE aud_id = NEW.scr_aud_id;
    
    -- Calcular capacidad del auditorio
    SET auditorium_capacity = total_rows * seats_per_row;
    
    -- Actualizar asientos disponibles
    UPDATE tb_screening 
    SET scr_available_seats = auditorium_capacity
    WHERE scr_id = NEW.scr_id;
    
    -- Crear tickets automáticamente para todos los asientos
    IF row_format = 'letters' THEN
        -- Generar asientos con filas en formato de letras
        WHILE i <= total_rows DO
            -- Convertir número de fila a letra (1=A, 2=B, ..., 26=Z, 27=AA, etc.)
            IF i <= 26 THEN
                SET current_row_letter = CHAR(64 + i);
            ELSE
                SET current_row_letter = CONCAT(CHAR(64 + FLOOR((i-1)/26)), CHAR(64 + ((i-1) % 26) + 1));
            END IF;
            
            SET j = 1;
            WHILE j <= seats_per_row DO
                INSERT INTO tb_ticket (tic_id, tic_row, tic_seat, tic_scr_id, tic_status)
                VALUES (UUID(), current_row_letter, j, NEW.scr_id, 'available');
                SET j = j + 1;
            END WHILE;
            
            SET i = i + 1;
        END WHILE;
    ELSE
        -- Generar asientos con filas numéricas (compatibilidad futura)
        WHILE i <= total_rows DO
            SET j = 1;
            WHILE j <= seats_per_row DO
                INSERT INTO tb_ticket (tic_id, tic_row, tic_seat, tic_scr_id, tic_status)
                VALUES (UUID(), CAST(i AS CHAR(2)), j, NEW.scr_id, 'available');
                SET j = j + 1;
            END WHILE;
            SET i = i + 1;
        END WHILE;
    END IF;
END//

-- Trigger para validar horarios antes de insertar
CREATE TRIGGER validate_screening_schedule
    BEFORE INSERT ON tb_screening
    FOR EACH ROW
BEGIN
    DECLARE movie_duration INT DEFAULT 0;
    DECLARE end_time TIME;
    DECLARE conflict_count INT DEFAULT 0;
    
    -- Obtener duración de la película
    SELECT mov_duration INTO movie_duration
    FROM tb_movie 
    WHERE mov_id = NEW.scr_mov_id;
    
    -- Calcular hora de finalización (duración en minutos)
    SET end_time = ADDTIME(NEW.scr_time, SEC_TO_TIME(movie_duration * 60));
    
    -- Verificar conflictos de horario en el mismo auditorio
    SELECT COUNT(*) INTO conflict_count
    FROM tb_screening s1
    JOIN tb_movie m1 ON s1.scr_mov_id = m1.mov_id
    WHERE s1.scr_aud_id = NEW.scr_aud_id
    AND s1.scr_date = NEW.scr_date
    AND s1.scr_status NOT IN ('cancelled')
    AND (
        -- Nueva función empieza durante una función existente
        (NEW.scr_time >= s1.scr_time AND NEW.scr_time <= ADDTIME(s1.scr_time, SEC_TO_TIME(m1.mov_duration * 60)))
        OR
        -- Nueva función termina durante una función existente
        (end_time >= s1.scr_time AND end_time <= ADDTIME(s1.scr_time, SEC_TO_TIME(m1.mov_duration * 60)))
        OR
        -- Nueva función cubre completamente una función existente
        (NEW.scr_time <= s1.scr_time AND end_time >= ADDTIME(s1.scr_time, SEC_TO_TIME(m1.mov_duration * 60)))
    );
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Conflicto de horario: el auditorio ya está ocupado en ese horario';
    END IF;
    
    -- Validar que la fecha no sea en el pasado
    IF NEW.scr_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se pueden programar funciones en fechas pasadas';
    END IF;
END//

-- Trigger para actualizar timestamp
CREATE TRIGGER update_screening_timestamp
    BEFORE UPDATE ON tb_screening
    FOR EACH ROW
BEGIN
    SET NEW.scr_updated = CURRENT_TIMESTAMP;
END//

DELIMITER ;
