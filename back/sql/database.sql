-- ============================================
-- CINEMA DATABASE SCHEMA
-- ============================================

-- Tabla de auditorios (debe crearse primero)
CREATE TABLE tb_auditorium (
    aud_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    aud_name VARCHAR(100) NOT NULL,
    aud_capacity INT NOT NULL CHECK (aud_capacity > 0),
    aud_total_rows INT NOT NULL CHECK (aud_total_rows > 0),
    aud_seats_per_row INT NOT NULL CHECK (aud_seats_per_row > 0),
    aud_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aud_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de películas
CREATE TABLE tb_movie (
    mov_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    mov_title VARCHAR(255) NOT NULL,
    mov_classification VARCHAR(10) NOT NULL CHECK (mov_classification IN ('G', 'PG', 'PG-13', 'R', 'NC-17')),
    mov_duration INT NOT NULL CHECK (mov_duration > 0),
    mov_description TEXT,
    mov_genre VARCHAR(100),
    mov_director VARCHAR(255),
    mov_release_date DATE,
    mov_poster_url TEXT,
    mov_status ENUM('active', 'inactive') DEFAULT 'active',
    mov_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mov_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de empleados
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

-- Tabla de usuarios/clientes
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

-- Tabla de proyecciones/funciones
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

-- Tabla de tickets/boletos
CREATE TABLE tb_ticket (
    tic_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    tic_row INT NOT NULL CHECK (tic_row > 0),
    tic_seat INT NOT NULL CHECK (tic_seat > 0),
    tic_scr_id CHAR(36) NOT NULL,
    tic_status ENUM('available', 'reserved', 'sold') DEFAULT 'available',
    tic_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tic_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tic_scr_id) REFERENCES tb_screening(scr_id) ON DELETE CASCADE,
    -- Un asiento por función (evitar duplicados)
    UNIQUE KEY unique_seat_per_screening (tic_scr_id, tic_row, tic_seat)
);

-- Tabla de ventas
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

-- ============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ============================================

-- Índices para búsquedas frecuentes
CREATE INDEX idx_movie_status ON tb_movie(mov_status);
CREATE INDEX idx_movie_classification ON tb_movie(mov_classification);
CREATE INDEX idx_screening_date ON tb_screening(scr_date);
CREATE INDEX idx_screening_movie ON tb_screening(scr_mov_id);
CREATE INDEX idx_screening_auditorium ON tb_screening(scr_aud_id);
CREATE INDEX idx_ticket_screening ON tb_ticket(tic_scr_id);
CREATE INDEX idx_sale_user ON tb_sale(sal_usr_id);
CREATE INDEX idx_sale_date ON tb_sale(sal_created);
CREATE INDEX idx_user_email ON tb_user(usr_email);
CREATE INDEX idx_employee_email ON tb_employee(emp_email);

-- ============================================
-- TRIGGERS PARA AUTOMATIZACIÓN
-- ============================================

-- Trigger para actualizar asientos disponibles cuando se vende un ticket
DELIMITER //
CREATE TRIGGER update_available_seats_after_sale
    AFTER INSERT ON tb_sale
    FOR EACH ROW
BEGIN
    IF NEW.sal_status = 'completed' THEN
        UPDATE tb_screening 
        SET scr_available_seats = scr_available_seats - 1
        WHERE scr_id = (
            SELECT tic_scr_id 
            FROM tb_ticket 
            WHERE tic_id = NEW.sal_tic_id
        );
        
        UPDATE tb_ticket 
        SET tic_status = 'sold'
        WHERE tic_id = NEW.sal_tic_id;
    END IF;
END//

-- Trigger para restaurar asientos cuando se cancela una venta
CREATE TRIGGER restore_available_seats_after_cancel
    AFTER UPDATE ON tb_sale
    FOR EACH ROW
BEGIN
    IF OLD.sal_status = 'completed' AND NEW.sal_status IN ('cancelled', 'refunded') THEN
        UPDATE tb_screening 
        SET scr_available_seats = scr_available_seats + 1
        WHERE scr_id = (
            SELECT tic_scr_id 
            FROM tb_ticket 
            WHERE tic_id = NEW.sal_tic_id
        );
        
        UPDATE tb_ticket 
        SET tic_status = 'available'
        WHERE tic_id = NEW.sal_tic_id;
    END IF;
END//

DELIMITER ;