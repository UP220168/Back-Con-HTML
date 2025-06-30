-- ============================================
-- TABLA DE PELÍCULAS - tb_movie (Simplificado)
-- ============================================

-- Creación de la tabla de películas
CREATE TABLE tb_movie (
    mov_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    mov_title VARCHAR(255) NOT NULL,
    mov_classification VARCHAR(10) NOT NULL CHECK (mov_classification IN ('G', 'PG', 'PG-13', 'R', 'NC-17')),
    mov_duration INT NOT NULL CHECK (mov_duration > 0),
    mov_description TEXT,
    mov_genre VARCHAR(100),
    mov_status ENUM('active', 'inactive') DEFAULT 'active',
    mov_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mov_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes en películas
CREATE INDEX idx_movie_status ON tb_movie(mov_status);
CREATE INDEX idx_movie_classification ON tb_movie(mov_classification);
CREATE INDEX idx_movie_genre ON tb_movie(mov_genre);
CREATE INDEX idx_movie_title ON tb_movie(mov_title);

-- Trigger para actualizar fecha de modificación
DELIMITER //
CREATE TRIGGER update_movie_timestamp
    BEFORE UPDATE ON tb_movie
    FOR EACH ROW
BEGIN
    SET NEW.mov_updated = CURRENT_TIMESTAMP;
END//

DELIMITER ;

-- Insertar datos de ejemplo
INSERT INTO tb_movie (mov_id, mov_title, mov_classification, mov_duration, mov_description, mov_genre, mov_status) VALUES
(UUID(), 'Avatar: El Camino del Agua', 'PG-13', 192, 'Secuela de la exitosa película de ciencia ficción', 'Ciencia Ficción', 'active'),
(UUID(), 'Top Gun: Maverick', 'PG-13', 130, 'Secuela de la película de acción de los 80s', 'Acción', 'active');