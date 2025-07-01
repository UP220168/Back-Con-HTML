from typing import List, Optional, Dict, Any
from db_connection import database
import uuid
from datetime import datetime, date

class ScreeningRepository:
    """Repository para manejar operaciones de base de datos de proyecciones"""
    
    def __init__(self):
        self.db = database
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener todas las proyecciones con paginación"""
        try:
            query = """
            SELECT scr_id, scr_mov_id, scr_aud_id, scr_date, scr_time, 
                   scr_price, scr_available_seats, scr_status, scr_created, scr_updated
            FROM tb_screening 
            WHERE scr_status != 'cancelled'
            ORDER BY scr_date DESC, scr_time DESC
            LIMIT %s OFFSET %s
            """
            result = self.db.execute_safe(query, (limit, skip))
            return result
        except Exception as e:
            raise Exception(f"Error getting screenings: {str(e)}")
    
    async def get_by_id(self, screening_id: str) -> Optional[Dict[str, Any]]:
        """Obtener proyección por ID"""
        try:
            query = """
            SELECT scr_id, scr_mov_id, scr_aud_id, scr_date, scr_time, 
                   scr_price, scr_available_seats, scr_status, scr_created, scr_updated
            FROM tb_screening 
            WHERE scr_id = %s
            """
            result = self.db.execute_safe(query, (screening_id,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error getting screening by ID: {str(e)}")
    
    async def create(self, screening_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nueva proyección"""
        try:
            screening_id = str(uuid.uuid4())
            now = datetime.now()
            
            query = """
            INSERT INTO tb_screening (scr_id, scr_mov_id, scr_aud_id, scr_date, scr_time, 
                                    scr_price, scr_status, scr_created, scr_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.db.execute_safe(query, (
                screening_id,
                screening_data['scr_mov_id'],
                screening_data['scr_aud_id'],
                screening_data['scr_date'],
                screening_data['scr_time'],
                screening_data['scr_price'],
                screening_data.get('scr_status', 'scheduled'),
                now,
                now
            ))
            
            # Devolver la proyección creada
            return await self.get_by_id(screening_id)
            
        except Exception as e:
            raise Exception(f"Error creating screening: {str(e)}")
    
    async def update(self, screening_id: str, screening_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar proyección existente"""
        try:
            # Verificar que la proyección existe
            existing = await self.get_by_id(screening_id)
            if not existing:
                return None
            
            # Construir query dinámicamente basado en campos proporcionados
            set_clauses = []
            values = []
            
            for field, value in screening_data.items():
                if field in ['scr_mov_id', 'scr_aud_id', 'scr_date', 'scr_time', 
                           'scr_price', 'scr_available_seats', 'scr_status']:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                return existing  # No hay nada que actualizar
            
            # Agregar timestamp de actualización
            set_clauses.append("scr_updated = %s")
            values.append(datetime.now())
            values.append(screening_id)  # Para el WHERE
            
            query = f"""
            UPDATE tb_screening 
            SET {', '.join(set_clauses)}
            WHERE scr_id = %s
            """
            
            self.db.execute_safe(query, tuple(values))
            
            # Devolver la proyección actualizada
            return await self.get_by_id(screening_id)
            
        except Exception as e:
            raise Exception(f"Error updating screening: {str(e)}")
    
    async def delete(self, screening_id: str) -> bool:
        """Eliminar proyección (soft delete - cambiar estado a cancelled)"""
        try:
            # Verificar que la proyección existe
            existing = await self.get_by_id(screening_id)
            if not existing:
                return False
            
            query = """
            UPDATE tb_screening 
            SET scr_status = 'cancelled', scr_updated = %s
            WHERE scr_id = %s
            """
            
            self.db.execute_safe(query, (datetime.now(), screening_id))
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting screening: {str(e)}")
    
    async def search(self, movie_id: str = None, auditorium_id: str = None, 
                    screening_date: date = None, status: str = None) -> List[Dict[str, Any]]:
        """Buscar proyecciones por criterios"""
        try:
            where_clauses = ["scr_status != 'cancelled'"]
            values = []
            
            if movie_id:
                where_clauses.append("scr_mov_id = %s")
                values.append(movie_id)
            
            if auditorium_id:
                where_clauses.append("scr_aud_id = %s")
                values.append(auditorium_id)
            
            if screening_date:
                where_clauses.append("scr_date = %s")
                values.append(screening_date)
            
            if status:
                where_clauses.append("scr_status = %s")
                values.append(status)
            
            query = f"""
            SELECT scr_id, scr_mov_id, scr_aud_id, scr_date, scr_time, 
                   scr_price, scr_available_seats, scr_status, scr_created, scr_updated
            FROM tb_screening 
            WHERE {' AND '.join(where_clauses)}
            ORDER BY scr_date DESC, scr_time DESC
            """
            
            result = self.db.execute_safe(query, tuple(values))
            return result
            
        except Exception as e:
            raise Exception(f"Error searching screenings: {str(e)}")
    
    async def count_total(self) -> int:
        """Contar total de proyecciones activas"""
        try:
            query = "SELECT COUNT(*) as total FROM tb_screening WHERE scr_status != 'cancelled'"
            result = self.db.execute_safe(query)
            return result[0]['total'] if result else 0
        except Exception as e:
            raise Exception(f"Error counting screenings: {str(e)}")
    
    async def update_available_seats(self, screening_id: str, seats_change: int) -> bool:
        """Actualizar asientos disponibles (para ventas de tickets)"""
        try:
            query = """
            UPDATE tb_screening 
            SET scr_available_seats = scr_available_seats + %s, scr_updated = %s
            WHERE scr_id = %s AND scr_available_seats + %s >= 0
            """
            
            affected_rows = self.db.execute_safe(query, (seats_change, datetime.now(), screening_id, seats_change))
            return affected_rows > 0
            
        except Exception as e:
            raise Exception(f"Error updating available seats: {str(e)}")

# Instancia global del repository
screening_repository = ScreeningRepository()
