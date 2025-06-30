from typing import List, Optional, Dict, Any
from models.screening import Screening
from db_connection import database

class ScreeningRepository:
    def __init__(self):
        self.db = database

    def create(self, screening_data: Dict[str, Any]) -> Screening:
        """Crear una nueva proyección"""
        query = """
        INSERT INTO tb_screening 
        (scr_mov_id, scr_aud_id, scr_date, scr_time, scr_price, scr_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            screening_data['scr_mov_id'],
            screening_data['scr_aud_id'],
            screening_data['scr_date'],
            screening_data['scr_time'],
            screening_data['scr_price'],
            screening_data.get('scr_status', 'scheduled')
        )
        
        screening_id = self.db.execute_with_return(query, params)
        
        if screening_id:
            return self.get_by_id(screening_id)
        return None

    def get_by_id(self, screening_id: str) -> Optional[Screening]:
        """Obtener proyección por ID"""
        query = "SELECT * FROM tb_screening WHERE scr_id = %s"
        result = self.db.execute_safe(query, (screening_id,))
        
        if result:
            return Screening(**result[0])
        return None

    def get_all(self) -> List[Screening]:
        """Obtener todas las proyecciones"""
        query = "SELECT * FROM tb_screening ORDER BY scr_date ASC, scr_time ASC"
        results = self.db.execute_safe(query)
        
        return [Screening(**row) for row in results]

    def get_by_movie(self, movie_id: str) -> List[Screening]:
        """Obtener proyecciones por película"""
        query = "SELECT * FROM tb_screening WHERE scr_mov_id = %s ORDER BY scr_date ASC, scr_time ASC"
        results = self.db.execute_safe(query, (movie_id,))
        
        return [Screening(**row) for row in results]

    def get_by_auditorium(self, auditorium_id: str) -> List[Screening]:
        """Obtener proyecciones por auditorio"""
        query = "SELECT * FROM tb_screening WHERE scr_aud_id = %s ORDER BY scr_date ASC, scr_time ASC"
        results = self.db.execute_safe(query, (auditorium_id,))
        
        return [Screening(**row) for row in results]

    def get_by_date(self, date: str) -> List[Screening]:
        """Obtener proyecciones por fecha"""
        query = "SELECT * FROM tb_screening WHERE scr_date = %s ORDER BY scr_time ASC"
        results = self.db.execute_safe(query, (date,))
        
        return [Screening(**row) for row in results]

    def get_by_status(self, status: str) -> List[Screening]:
        """Obtener proyecciones por estado"""
        query = "SELECT * FROM tb_screening WHERE scr_status = %s ORDER BY scr_date ASC, scr_time ASC"
        results = self.db.execute_safe(query, (status,))
        
        return [Screening(**row) for row in results]

    def update(self, screening_id: str, screening_data: Dict[str, Any]) -> Optional[Screening]:
        """Actualizar proyección"""
        # Construir query de actualización dinámicamente
        set_clauses = []
        params = []
        
        for key, value in screening_data.items():
            if value is not None:
                set_clauses.append(f"{key} = %s")
                params.append(value)
        
        if not set_clauses:
            return self.get_by_id(screening_id)
        
        # Agregar timestamp de actualización
        set_clauses.append("scr_updated = CURRENT_TIMESTAMP")
        params.append(screening_id)
        
        query = f"UPDATE tb_screening SET {', '.join(set_clauses)} WHERE scr_id = %s"
        
        success = self.db.execute_safe(query, tuple(params))
        
        if success:
            return self.get_by_id(screening_id)
        return None

    def delete(self, screening_id: str) -> bool:
        """Eliminar proyección"""
        query = "DELETE FROM tb_screening WHERE scr_id = %s"
        return self.db.execute_safe(query, (screening_id,)) is not None

    def update_available_seats(self, screening_id: str, seats: int) -> bool:
        """Actualizar asientos disponibles"""
        query = "UPDATE tb_screening SET scr_available_seats = %s WHERE scr_id = %s"
        return self.db.execute_safe(query, (seats, screening_id)) is not None
