-- ============================================
-- TABLA DE VENTAS - tb_sale
-- ============================================

-- Creación de la tabla de ventas
CREATE TABLE tb_sale (
    sal_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    sal_usr_id CHAR(36) NOT NULL,
    sal_emp_id CHAR(36) NOT NULL,
    sal_tic_id CHAR(36) NOT NULL,
    sal_total_amount DECIMAL(10,2) NOT NULL CHECK (sal_total_amount > 0),
    sal_payment_method ENUM('cash', 'card', 'digital') NOT NULL,
    sal_status ENUM('pending', 'completed', 'cancelled', 'refunded') DEFAULT 'pending',
    sal_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sal_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sal_usr_id) REFERENCES tb_user(usr_id) ON DELETE CASCADE,
    FOREIGN KEY (sal_emp_id) REFERENCES tb_employee(emp_id) ON DELETE CASCADE,
    FOREIGN KEY (sal_tic_id) REFERENCES tb_ticket(tic_id) ON DELETE CASCADE,
    -- Un ticket solo puede venderse una vez
    UNIQUE KEY unique_ticket_sale (sal_tic_id)
);

-- Índices para búsquedas frecuentes en ventas
CREATE INDEX idx_sale_user ON tb_sale(sal_usr_id);
CREATE INDEX idx_sale_employee ON tb_sale(sal_emp_id);
CREATE INDEX idx_sale_ticket ON tb_sale(sal_tic_id);
CREATE INDEX idx_sale_date ON tb_sale(sal_created);
CREATE INDEX idx_sale_status ON tb_sale(sal_status);
CREATE INDEX idx_sale_payment_method ON tb_sale(sal_payment_method);
CREATE INDEX idx_sale_amount ON tb_sale(sal_total_amount);

-- Trigger para validar venta antes de insertar
DELIMITER //
CREATE TRIGGER validate_sale_insert
    BEFORE INSERT ON tb_sale
    FOR EACH ROW
BEGIN
    DECLARE ticket_status ENUM('available', 'reserved', 'sold');
    DECLARE user_status ENUM('active', 'inactive');
    DECLARE emp_status ENUM('active', 'inactive');
    DECLARE screening_status ENUM('scheduled', 'ongoing', 'finished', 'cancelled');
    
    -- Verificar estado del ticket
    SELECT t.tic_status, s.scr_status 
    INTO ticket_status, screening_status
    FROM tb_ticket t
    JOIN tb_screening s ON t.tic_scr_id = s.scr_id
    WHERE t.tic_id = NEW.sal_tic_id;
    
    IF ticket_status NOT IN ('available', 'reserved') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El ticket no está disponible para la venta';
    END IF;
    
    IF screening_status NOT IN ('scheduled', 'ongoing') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede vender ticket para esta función';
    END IF;
    
    -- Verificar estado del usuario
    SELECT usr_status INTO user_status
    FROM tb_user 
    WHERE usr_id = NEW.sal_usr_id;
    
    IF user_status != 'active' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario no está activo';
    END IF;
    
    -- Verificar estado del empleado
    SELECT emp_status INTO emp_status
    FROM tb_employee 
    WHERE emp_id = NEW.sal_emp_id;
    
    IF emp_status != 'active' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado no está activo';
    END IF;
END//

-- Trigger para actualizar estado del ticket cuando se completa la venta
CREATE TRIGGER update_ticket_on_sale_complete
    AFTER UPDATE ON tb_sale
    FOR EACH ROW
BEGIN
    -- Si la venta se completa, marcar ticket como vendido
    IF NEW.sal_status = 'completed' AND OLD.sal_status != 'completed' THEN
        UPDATE tb_ticket 
        SET tic_status = 'sold',
            tic_updated = CURRENT_TIMESTAMP
        WHERE tic_id = NEW.sal_tic_id;
    END IF;
    
    -- Si la venta se cancela o reembolsa, liberar el ticket
    IF NEW.sal_status IN ('cancelled', 'refunded') AND OLD.sal_status = 'completed' THEN
        UPDATE tb_ticket 
        SET tic_status = 'available',
            tic_updated = CURRENT_TIMESTAMP
        WHERE tic_id = NEW.sal_tic_id;
    END IF;
END//

-- Trigger para actualizar timestamp
CREATE TRIGGER update_sale_timestamp
    BEFORE UPDATE ON tb_sale
    FOR EACH ROW
BEGIN
    SET NEW.sal_updated = CURRENT_TIMESTAMP;
END//

DELIMITER ;
