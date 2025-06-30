-- ============================================
-- TABLA DE EMPLEADOS - tb_employee
-- ============================================

-- Creación de la tabla de empleados
CREATE TABLE tb_employee (
    emp_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    emp_name VARCHAR(255) NOT NULL,
    emp_email VARCHAR(255) NOT NULL UNIQUE,
    emp_position ENUM('admin', 'employee', 'manager') NOT NULL DEFAULT 'employee',
    emp_password_hash VARCHAR(255) NOT NULL,
    emp_phone VARCHAR(20),
    emp_status ENUM('active', 'inactive') DEFAULT 'active',
    emp_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    emp_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes en empleados
CREATE INDEX idx_employee_email ON tb_employee(emp_email);
CREATE INDEX idx_employee_position ON tb_employee(emp_position);
CREATE INDEX idx_employee_status ON tb_employee(emp_status);
CREATE INDEX idx_employee_name ON tb_employee(emp_name);

-- Trigger para validar email antes de insertar
DELIMITER //
CREATE TRIGGER validate_employee_email_insert
    BEFORE INSERT ON tb_employee
    FOR EACH ROW
BEGIN
    -- Validar formato básico de email
    IF NEW.emp_email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Formato de email inválido';
    END IF;
    
    -- Convertir email a minúsculas
    SET NEW.emp_email = LOWER(NEW.emp_email);
END//

-- Trigger para validar email antes de actualizar
CREATE TRIGGER validate_employee_email_update
    BEFORE UPDATE ON tb_employee
    FOR EACH ROW
BEGIN
    -- Validar formato básico de email
    IF NEW.emp_email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Formato de email inválido';
    END IF;
    
    -- Convertir email a minúsculas
    SET NEW.emp_email = LOWER(NEW.emp_email);
    
    -- Actualizar timestamp
    SET NEW.emp_updated = CURRENT_TIMESTAMP;
END//

DELIMITER ;

-- Insertar datos de ejemplo
INSERT INTO tb_employee (emp_id, emp_name, emp_email, emp_position, emp_password_hash, emp_status) VALUES
(UUID(), 'Administrador', 'admin@cinema.com', 'admin', SHA2('admin123', 256), 'active');