-- ============================================
-- TABLA DE USUARIOS/CLIENTES - tb_user
-- ============================================

-- Creación de la tabla de usuarios
CREATE TABLE tb_user (
    usr_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    usr_name VARCHAR(255) NOT NULL,
    usr_email VARCHAR(255) NOT NULL UNIQUE,
    usr_password_hash VARCHAR(255) NOT NULL,
    usr_phone VARCHAR(20),
    usr_birth_date DATE,
    usr_status ENUM('active', 'inactive') DEFAULT 'active',
    usr_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usr_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes en usuarios
CREATE INDEX idx_user_email ON tb_user(usr_email);
CREATE INDEX idx_user_status ON tb_user(usr_status);
CREATE INDEX idx_user_name ON tb_user(usr_name);
CREATE INDEX idx_user_birth_date ON tb_user(usr_birth_date);

-- Trigger para validar email y edad antes de insertar
DELIMITER //
CREATE TRIGGER validate_user_insert
    BEFORE INSERT ON tb_user
    FOR EACH ROW
BEGIN
    -- Validar formato básico de email
    IF NEW.usr_email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Formato de email inválido';
    END IF;
    
    -- Validar edad mínima (13 años)
    IF NEW.usr_birth_date IS NOT NULL AND DATEDIFF(CURDATE(), NEW.usr_birth_date) < 4745 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario debe tener al menos 13 años';
    END IF;
    
    -- Convertir email a minúsculas
    SET NEW.usr_email = LOWER(NEW.usr_email);
END//

-- Trigger para validar email y edad antes de actualizar
CREATE TRIGGER validate_user_update
    BEFORE UPDATE ON tb_user
    FOR EACH ROW
BEGIN
    -- Validar formato básico de email
    IF NEW.usr_email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Formato de email inválido';
    END IF;
    
    -- Validar edad mínima (13 años)
    IF NEW.usr_birth_date IS NOT NULL AND DATEDIFF(CURDATE(), NEW.usr_birth_date) < 4745 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario debe tener al menos 13 años';
    END IF;
    
    -- Convertir email a minúsculas
    SET NEW.usr_email = LOWER(NEW.usr_email);
    
    -- Actualizar timestamp
    SET NEW.usr_updated = CURRENT_TIMESTAMP;
END//

DELIMITER ;
