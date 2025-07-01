from typing import List, Optional, Dict, Any
from db_connection import database
import uuid
from datetime import datetime

class MovieRepository:
    """Repository para manejar operaciones de base de datos de películas"""
    
    def __init__(self):
        self.db = database
    
    async def get_all(self, skip: int = 0, limit: int = 100, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Obtener todas las películas con paginación"""
        try:
            print(f"🎬 Repository get_all called with: skip={skip}, limit={limit}, include_inactive={include_inactive}")
            
            if include_inactive:
                # Obtener todas las películas (activas e inactivas)
                query = """
                SELECT mov_id, mov_title, mov_classification, mov_duration, 
                       mov_description, mov_genre, mov_status, mov_created, mov_updated
                FROM tb_movie 
                ORDER BY mov_status DESC, mov_created DESC
                LIMIT %s OFFSET %s
                """
                print("🎬 Using query for ALL movies (active + inactive)")
            else:
                # Solo películas activas (comportamiento original)
                query = """
                SELECT mov_id, mov_title, mov_classification, mov_duration, 
                       mov_description, mov_genre, mov_status, mov_created, mov_updated
                FROM tb_movie 
                WHERE mov_status = 'active'
                ORDER BY mov_created DESC
                LIMIT %s OFFSET %s
                """
                print("🎬 Using query for ACTIVE movies only")
            
            result = self.db.execute_safe(query, (limit, skip))
            print(f"🎬 Repository returned {len(result)} movies")
            
            # Debug: mostrar estado de cada película
            for movie in result:
                print(f"  - {movie['mov_title']}: {movie['mov_status']}")
            
            return result
            return result
        except Exception as e:
            raise Exception(f"Error getting movies: {str(e)}")
    
    async def get_by_id(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """Obtener película por ID"""
        try:
            query = """
            SELECT mov_id, mov_title, mov_classification, mov_duration, 
                   mov_description, mov_genre, mov_status, mov_created, mov_updated
            FROM tb_movie 
            WHERE mov_id = %s
            """
            result = self.db.execute_safe(query, (movie_id,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error getting movie by ID: {str(e)}")
    
    async def create(self, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nueva película"""
        try:
            movie_id = str(uuid.uuid4())
            now = datetime.now()
            
            query = """
            INSERT INTO tb_movie (mov_id, mov_title, mov_classification, mov_duration, 
                                mov_description, mov_genre, mov_status, mov_created, mov_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.db.execute_safe(query, (
                movie_id,
                movie_data['mov_title'],
                movie_data['mov_classification'],
                movie_data['mov_duration'],
                movie_data.get('mov_description'),
                movie_data.get('mov_genre'),
                'active',
                now,
                now
            ))
            
            # Devolver la película creada
            return await self.get_by_id(movie_id)
            
        except Exception as e:
            raise Exception(f"Error creating movie: {str(e)}")
    
    async def update(self, movie_id: str, movie_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar película existente"""
        try:
            # Verificar que la película existe
            existing = await self.get_by_id(movie_id)
            if not existing:
                return None
            
            # Construir query dinámicamente basado en campos proporcionados
            set_clauses = []
            values = []
            
            for field, value in movie_data.items():
                if field in ['mov_title', 'mov_classification', 'mov_duration', 
                           'mov_description', 'mov_genre', 'mov_status']:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                return existing  # No hay nada que actualizar
            
            # Agregar timestamp de actualización
            set_clauses.append("mov_updated = %s")
            values.append(datetime.now())
            values.append(movie_id)  # Para el WHERE
            
            query = f"""
            UPDATE tb_movie 
            SET {', '.join(set_clauses)}
            WHERE mov_id = %s
            """
            
            self.db.execute_safe(query, tuple(values))
            
            # Devolver la película actualizada
            return await self.get_by_id(movie_id)
            
        except Exception as e:
            raise Exception(f"Error updating movie: {str(e)}")
    
    async def delete(self, movie_id: str) -> bool:
        """Eliminar película (soft delete)"""
        try:
            # Verificar que la película existe
            existing = await self.get_by_id(movie_id)
            if not existing:
                return False
            
            query = """
            UPDATE tb_movie 
            SET mov_status = 'inactive', mov_updated = %s
            WHERE mov_id = %s
            """
            
            self.db.execute_safe(query, (datetime.now(), movie_id))
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting movie: {str(e)}")
    
    async def search(self, title: str = None, genre: str = None, classification: str = None) -> List[Dict[str, Any]]:
        """Buscar películas por criterios"""
        try:
            where_clauses = ["mov_status = 'active'"]
            values = []
            
            if title:
                where_clauses.append("mov_title LIKE %s")
                values.append(f"%{title}%")
            
            if genre:
                where_clauses.append("mov_genre LIKE %s")
                values.append(f"%{genre}%")
            
            if classification:
                where_clauses.append("mov_classification = %s")
                values.append(classification)
            
            query = f"""
            SELECT mov_id, mov_title, mov_classification, mov_duration, 
                   mov_description, mov_genre, mov_status, mov_created, mov_updated
            FROM tb_movie 
            WHERE {' AND '.join(where_clauses)}
            ORDER BY mov_created DESC
            """
            
            result = self.db.execute_safe(query, tuple(values))
            return result
            
        except Exception as e:
            raise Exception(f"Error searching movies: {str(e)}")
    
    async def count_total(self, include_inactive: bool = False) -> int:
        """Contar total de películas"""
        try:
            if include_inactive:
                query = "SELECT COUNT(*) as total FROM tb_movie"
            else:
                query = "SELECT COUNT(*) as total FROM tb_movie WHERE mov_status = 'active'"
            result = self.db.execute_safe(query)
            return result[0]['total'] if result else 0
        except Exception as e:
            raise Exception(f"Error counting movies: {str(e)}")

# Instancia global del repository
movie_repository = MovieRepository()
