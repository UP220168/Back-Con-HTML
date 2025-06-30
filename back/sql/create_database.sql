-- ============================================
-- SCRIPT MAESTRO - CREACIÓN COMPLETA DE BASE DE DATOS
-- ============================================
-- 
-- Este archivo ejecuta todos los scripts de creación de tablas
-- en el orden correcto para respetar las dependencias de claves foráneas
--
-- ORDEN DE EJECUCIÓN:
-- 1. tb_auditorium (no tiene dependencias)
-- 2. tb_movie (no tiene dependencias)  
-- 3. tb_employee (no tiene dependencias)
-- 4. tb_user (no tiene dependencias)
-- 5. tb_screening (depende de tb_movie y tb_auditorium)
-- 6. tb_ticket (depende de tb_screening)
-- 7. tb_sale (depende de tb_user, tb_employee y tb_ticket)
--
-- ============================================

-- Configuración inicial
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';
SET time_zone = '+00:00';

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS cinema_foraneo_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE cinema_foraneo_db;

-- ============================================
-- EJECUTAR SCRIPTS EN ORDEN
-- ============================================

-- 1. AUDITORIOS (sin dependencias)
SOURCE tb_auditorium.sql;

-- 2. PELÍCULAS (sin dependencias)
SOURCE tb_movie.sql;

-- 3. EMPLEADOS (sin dependencias)
SOURCE tb_employee.sql;

-- 4. USUARIOS (sin dependencias)
SOURCE tb_user.sql;

-- 5. PROYECCIONES (depende de movies y auditoriums)
SOURCE tb_screening.sql;

-- 6. TICKETS (depende de screenings)
SOURCE tb_ticket.sql;

-- 7. VENTAS (depende de users, employees y tickets)
SOURCE tb_sale.sql;

-- Restaurar configuración
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- DATOS DE EJEMPLO (OPCIONAL)
-- ============================================

-- Insertar auditorios de ejemplo
INSERT INTO tb_auditorium (aud_id, aud_name, aud_total_rows, aud_seats_per_row, aud_row_format) VALUES
(UUID(), 'Sala 1', 10, 10, 'letters'),
(UUID(), 'Sala 2', 15, 10, 'letters'),
(UUID(), 'Sala VIP', 5, 10, 'letters');

-- Insertar empleado administrador por defecto
INSERT INTO tb_employee (emp_id, emp_name, emp_email, emp_position, emp_password_hash, emp_status) VALUES
(UUID(), 'Administrador', 'admin@cinema.com', 'admin', SHA2('admin123', 256), 'active');

-- Insertar películas de ejemplo
INSERT INTO tb_movie (mov_id, mov_title, mov_classification, mov_duration, mov_description, mov_genre, mov_status) VALUES
(UUID(), 'Avatar: El Camino del Agua', 'PG-13', 192, 'Secuela de la exitosa película de ciencia ficción', 'Ciencia Ficción', 'active'),
(UUID(), 'Top Gun: Maverick', 'PG-13', 130, 'Secuela de la película de acción de los 80s', 'Acción', 'active');

-- ============================================
-- VERIFICACIÓN DE INSTALACIÓN
-- ============================================

-- Mostrar resumen de tablas creadas
SELECT 
    TABLE_NAME as 'Tabla',
    TABLE_ROWS as 'Registros',
    CREATE_TIME as 'Fecha Creación'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'cinema_foraneo_db'
ORDER BY TABLE_NAME;

-- Mostrar triggers creados
SELECT 
    TRIGGER_NAME as 'Trigger',
    EVENT_MANIPULATION as 'Evento',
    EVENT_OBJECT_TABLE as 'Tabla'
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = 'cinema_foraneo_db'
ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME;

PRINT '============================================';
PRINT 'BASE DE DATOS CINEMA CREADA EXITOSAMENTE';
PRINT '============================================';
PRINT 'Tablas creadas: 7';
PRINT 'Triggers: 15+';
PRINT 'Formato de filas: LETRAS (A-Z, AA-ZZ)';
PRINT '============================================';
