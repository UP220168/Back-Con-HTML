from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from models.movie import MovieCreate, MovieUpdate, MovieResponse, MovieSummary
from repositories.movie_repository import movie_repository
import logging

logger = logging.getLogger(__name__)

class MovieService:
    """Service para lógica de negocio de películas"""
    
    def __init__(self):
        self.repository = movie_repository
    
    async def get_movies(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Obtener lista de películas con paginación"""
        try:
            # Validar parámetros
            if skip < 0:
                raise HTTPException(status_code=400, detail="Skip debe ser >= 0")
            if limit <= 0 or limit > 100:
                raise HTTPException(status_code=400, detail="Limit debe estar entre 1 y 100")
            
            # Obtener películas y total
            movies = await self.repository.get_all(skip, limit)
            total = await self.repository.count_total()
            
            # Convertir a modelos Pydantic
            movie_list = [self._dict_to_movie_summary(movie) for movie in movies]
            
            return {
                "movies": movie_list,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_movies: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def get_movie_by_id(self, movie_id: str) -> MovieResponse:
        """Obtener película por ID"""
        try:
            # Validar formato UUID (básico)
            if not movie_id or len(movie_id) < 30:
                raise HTTPException(status_code=400, detail="ID de película inválido")
            
            movie = await self.repository.get_by_id(movie_id)
            if not movie:
                raise HTTPException(status_code=404, detail="Película no encontrada")
            
            return self._dict_to_movie_response(movie)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_movie_by_id: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def create_movie(self, movie_data: MovieCreate) -> MovieResponse:
        """Crear nueva película"""
        try:
            # Validaciones de negocio adicionales
            await self._validate_movie_data(movie_data.dict())
            
            # Crear película
            created_movie = await self.repository.create(movie_data.dict())
            
            if not created_movie:
                raise HTTPException(status_code=500, detail="Error creando película")
            
            return self._dict_to_movie_response(created_movie)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in create_movie: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def update_movie(self, movie_id: str, movie_data: MovieUpdate) -> MovieResponse:
        """Actualizar película existente"""
        try:
            # Validar ID
            if not movie_id:
                raise HTTPException(status_code=400, detail="ID de película requerido")
            
            # Solo incluir campos que no son None
            update_data = {k: v for k, v in movie_data.dict().items() if v is not None}
            
            if not update_data:
                raise HTTPException(status_code=400, detail="No hay datos para actualizar")
            
            # Validaciones de negocio
            await self._validate_movie_data(update_data, is_update=True)
            
            # Actualizar
            updated_movie = await self.repository.update(movie_id, update_data)
            
            if not updated_movie:
                raise HTTPException(status_code=404, detail="Película no encontrada")
            
            return self._dict_to_movie_response(updated_movie)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in update_movie: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def delete_movie(self, movie_id: str) -> Dict[str, str]:
        """Eliminar película (soft delete)"""
        try:
            if not movie_id:
                raise HTTPException(status_code=400, detail="ID de película requerido")
            
            success = await self.repository.delete(movie_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Película no encontrada")
            
            return {"message": "Película eliminada exitosamente"}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in delete_movie: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def search_movies(self, title: str = None, genre: str = None, classification: str = None) -> List[MovieSummary]:
        """Buscar películas por criterios"""
        try:
            if not any([title, genre, classification]):
                raise HTTPException(status_code=400, detail="Debe proporcionar al menos un criterio de búsqueda")
            
            movies = await self.repository.search(title, genre, classification)
            
            return [self._dict_to_movie_summary(movie) for movie in movies]
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in search_movies: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    # Métodos auxiliares privados
    async def _validate_movie_data(self, data: Dict[str, Any], is_update: bool = False):
        """Validaciones de negocio adicionales"""
        # Validar duración
        if 'mov_duration' in data:
            if data['mov_duration'] <= 0 or data['mov_duration'] > 600:
                raise HTTPException(
                    status_code=400, 
                    detail="La duración debe estar entre 1 y 600 minutos"
                )
        
        # Validar título único (solo en creación por ahora)
        if 'mov_title' in data and not is_update:
            # Aquí podrías agregar validación de título único
            pass
    
    def _dict_to_movie_response(self, movie_dict: Dict[str, Any]) -> MovieResponse:
        """Convertir diccionario a modelo MovieResponse"""
        return MovieResponse(**movie_dict)
    
    def _dict_to_movie_summary(self, movie_dict: Dict[str, Any]) -> MovieSummary:
        """Convertir diccionario a modelo MovieSummary"""
        return MovieSummary(**movie_dict)

# Instancia global del service
movie_service = MovieService()
