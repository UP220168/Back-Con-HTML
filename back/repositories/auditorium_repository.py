from typing import List, Optional, Dict, Any
from db_connection import database
import uuid
from datetime import datetime

class AuditoriumRepository:
    """Repository para manejar operaciones de base de datos de auditorios"""
    
    def __init__(self):
        self.db = database
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener todos los auditorios con paginación"""
        try:
            query = """
            SELECT aud_id, aud_name, aud_total_rows, aud_seats_per_row, 
                   aud_row_format, aud_created, aud_updated,
                   (aud_total_rows * aud_seats_per_row) as total_capacity
            FROM tb_auditorium 
            ORDER BY aud_name
            LIMIT %s OFFSET %s
            """
            result = self.db.execute_safe(query, (limit, skip))
            return result
        except Exception as e:
            raise Exception(f"Error getting auditoriums: {str(e)}")
    
    async def get_by_id(self, auditorium_id: str) -> Optional[Dict[str, Any]]:
        """Obtener auditorio por ID"""
        try:
            query = """
            SELECT aud_id, aud_name, aud_total_rows, aud_seats_per_row, 
                   aud_row_format, aud_created, aud_updated,
                   (aud_total_rows * aud_seats_per_row) as total_capacity
            FROM tb_auditorium 
            WHERE aud_id = %s
            """
            result = self.db.execute_safe(query, (auditorium_id,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error getting auditorium by ID: {str(e)}")
    
    async def create(self, auditorium_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo auditorio"""
        try:
            auditorium_id = str(uuid.uuid4())
            now = datetime.now()
            
            query = """
            INSERT INTO tb_auditorium (aud_id, aud_name, aud_total_rows, aud_seats_per_row, 
                                     aud_row_format, aud_created, aud_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            self.db.execute_safe(query, (
                auditorium_id,
                auditorium_data['aud_name'],
                auditorium_data['aud_total_rows'],
                auditorium_data['aud_seats_per_row'],
                auditorium_data['aud_row_format'],
                now,
                now
            ))
            
            # Devolver el auditorio creado
            return await self.get_by_id(auditorium_id)
            
        except Exception as e:
            raise Exception(f"Error creating auditorium: {str(e)}")
    
    async def update(self, auditorium_id: str, auditorium_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar auditorio existente"""
        try:
            # Verificar que el auditorio existe
            existing = await self.get_by_id(auditorium_id)
            if not existing:
                return None
            
            # Construir query dinámicamente
            set_clauses = []
            values = []
            
            for field, value in auditorium_data.items():
                if field in ['aud_name', 'aud_total_rows', 'aud_seats_per_row', 'aud_row_format']:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                return existing
            
            set_clauses.append("aud_updated = %s")
            values.append(datetime.now())
            values.append(auditorium_id)
            
            query = f"""
            UPDATE tb_auditorium 
            SET {', '.join(set_clauses)}
            WHERE aud_id = %s
            """
            
            self.db.execute_safe(query, tuple(values))
            return await self.get_by_id(auditorium_id)
            
        except Exception as e:
            raise Exception(f"Error updating auditorium: {str(e)}")
    
    async def delete(self, auditorium_id: str) -> bool:
        """Eliminar auditorio"""
        try:
            # Verificar que el auditorio existe
            existing = await self.get_by_id(auditorium_id)
            if not existing:
                return False
            
            # Verificar que no tenga proyecciones asociadas
            check_query = "SELECT COUNT(*) as count FROM tb_screening WHERE scr_auditorium_id = %s"
            screenings = self.db.execute_safe(check_query, (auditorium_id,))
            
            if screenings and screenings[0]['count'] > 0:
                raise Exception("No se puede eliminar: el auditorio tiene proyecciones asociadas")
            
            query = "DELETE FROM tb_auditorium WHERE aud_id = %s"
            self.db.execute_safe(query, (auditorium_id,))
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting auditorium: {str(e)}")
    
    async def search_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Buscar auditorios por nombre"""
        try:
            query = """
            SELECT aud_id, aud_name, aud_total_rows, aud_seats_per_row, 
                   aud_row_format, aud_created, aud_updated,
                   (aud_total_rows * aud_seats_per_row) as total_capacity
            FROM tb_auditorium 
            WHERE aud_name LIKE %s
            ORDER BY aud_name
            """
            result = self.db.execute_safe(query, (f"%{name}%",))
            return result
        except Exception as e:
            raise Exception(f"Error searching auditoriums: {str(e)}")
    
    async def count_total(self) -> int:
        """Contar total de auditorios"""
        try:
            query = "SELECT COUNT(*) as total FROM tb_auditorium"
            result = self.db.execute_safe(query)
            return result[0]['total'] if result else 0
        except Exception as e:
            raise Exception(f"Error counting auditoriums: {str(e)}")

# Instancia global del repository
auditorium_repository = AuditoriumRepository()
