from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from models.screening import ScreeningCreate, ScreeningUpdate, ScreeningResponse, ScreeningSummary
from repositories.screening_repository import screening_repository
from repositories.movie_repository import movie_repository
from repositories.auditorium_repository import auditorium_repository
import logging
from datetime import date, time, datetime, timedelta

logger = logging.getLogger(__name__)

class ScreeningService:
    """Service para lógica de negocio de proyecciones"""
    
    def __init__(self):
        self.repository = screening_repository
        self.movie_repository = movie_repository
        self.auditorium_repository = auditorium_repository
    
    async def get_screenings(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Obtener lista de proyecciones con paginación"""
        try:
            # Validar parámetros
            if skip < 0:
                raise HTTPException(status_code=400, detail="Skip debe ser >= 0")
            if limit <= 0 or limit > 100:
                raise HTTPException(status_code=400, detail="Limit debe estar entre 1 y 100")
            
            # Obtener proyecciones y total
            screenings = await self.repository.get_all(skip, limit)
            total = await self.repository.count_total()
            
            # Convertir a modelos Pydantic
            screening_list = [self._dict_to_screening_summary(screening) for screening in screenings]
            
            return {
                "screenings": screening_list,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_screenings: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def get_screening_by_id(self, screening_id: str) -> ScreeningResponse:
        """Obtener proyección por ID"""
        try:
            # Validar formato UUID (básico)
            if not screening_id or len(screening_id) < 30:
                raise HTTPException(status_code=400, detail="ID de proyección inválido")
            
            screening = await self.repository.get_by_id(screening_id)
            if not screening:
                raise HTTPException(status_code=404, detail="Proyección no encontrada")
            
            return self._dict_to_screening_response(screening)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_screening_by_id: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def create_screening(self, screening_data: ScreeningCreate) -> ScreeningResponse:
        """Crear nueva proyección"""
        try:
            logger.info(f"Creating screening with data: {screening_data.dict()}")
            
            # Validaciones de negocio adicionales
            await self._validate_screening_data(screening_data.dict())
            logger.info("Basic validations passed")
            
            # Verificar que la película existe
            movie = await self.movie_repository.get_by_id(screening_data.scr_mov_id)
            if not movie:
                logger.error(f"Movie not found: {screening_data.scr_mov_id}")
                raise HTTPException(status_code=400, detail="La película especificada no existe")
            logger.info(f"Movie found: {movie.get('mov_title', 'Unknown')}")
            
            # Verificar que el auditorio existe
            auditorium = await self.auditorium_repository.get_by_id(screening_data.scr_aud_id)
            if not auditorium:
                logger.error(f"Auditorium not found: {screening_data.scr_aud_id}")
                raise HTTPException(status_code=400, detail="El auditorio especificado no existe")
            logger.info(f"Auditorium found: {auditorium.get('aud_name', 'Unknown')}")
            
            # Verificar conflictos de horario
            logger.info("Checking schedule conflicts...")
            await self._check_schedule_conflicts(screening_data)
            logger.info("No schedule conflicts found")
            
            # Crear proyección
            logger.info("Creating screening in database...")
            created_screening = await self.repository.create(screening_data.dict())
            
            if not created_screening:
                logger.error("Failed to create screening - repository returned None")
                raise HTTPException(status_code=500, detail="Error creando proyección")
            
            logger.info(f"Screening created successfully with ID: {created_screening.get('scr_id')}")
            return self._dict_to_screening_response(created_screening)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in create_screening: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    
    async def update_screening(self, screening_id: str, screening_data: ScreeningUpdate) -> ScreeningResponse:
        """Actualizar proyección existente"""
        try:
            # Validar ID
            if not screening_id:
                raise HTTPException(status_code=400, detail="ID de proyección requerido")
            
            # Solo incluir campos que no son None
            update_data = {k: v for k, v in screening_data.dict().items() if v is not None}
            
            if not update_data:
                raise HTTPException(status_code=400, detail="No hay datos para actualizar")
            
            # Validaciones de negocio
            await self._validate_screening_data(update_data, is_update=True)
            
            # Actualizar
            updated_screening = await self.repository.update(screening_id, update_data)
            
            if not updated_screening:
                raise HTTPException(status_code=404, detail="Proyección no encontrada")
            
            return self._dict_to_screening_response(updated_screening)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in update_screening: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def delete_screening(self, screening_id: str) -> Dict[str, str]:
        """Eliminar proyección (soft delete)"""
        try:
            if not screening_id:
                raise HTTPException(status_code=400, detail="ID de proyección requerido")
            
            success = await self.repository.delete(screening_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Proyección no encontrada")
            
            return {"message": "Proyección eliminada exitosamente"}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in delete_screening: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def search_screenings(self, movie_id: str = None, auditorium_id: str = None, 
                               screening_date: date = None, status: str = None) -> List[ScreeningSummary]:
        """Buscar proyecciones por criterios"""
        try:
            if not any([movie_id, auditorium_id, screening_date, status]):
                raise HTTPException(status_code=400, detail="Debe proporcionar al menos un criterio de búsqueda")
            
            screenings = await self.repository.search(movie_id, auditorium_id, screening_date, status)
            
            return [self._dict_to_screening_summary(screening) for screening in screenings]
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in search_screenings: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def get_available_seats(self, screening_id: str) -> int:
        """Obtener asientos disponibles para una proyección"""
        try:
            screening = await self.repository.get_by_id(screening_id)
            if not screening:
                raise HTTPException(status_code=404, detail="Proyección no encontrada")
            
            return screening['scr_available_seats']
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_available_seats: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    # Métodos auxiliares privados
    async def _validate_screening_data(self, data: Dict[str, Any], is_update: bool = False):
        """Validaciones de negocio adicionales"""
        # Validar precio
        if 'scr_price' in data:
            if data['scr_price'] <= 0:
                raise HTTPException(
                    status_code=400, 
                    detail="El precio debe ser mayor a 0"
                )
        
        # Validar fecha no en el pasado
        if 'scr_date' in data:
            screening_date = data['scr_date']
            if isinstance(screening_date, str):
                screening_date = datetime.strptime(screening_date, '%Y-%m-%d').date()
            
            # Permitir el día actual y fechas futuras
            if screening_date < date.today():
                raise HTTPException(
                    status_code=400, 
                    detail="No se puede programar una proyección en el pasado"
                )
    
    async def _check_schedule_conflicts(self, screening_data: ScreeningCreate, exclude_screening_id: str = None):
        """Verificar conflictos de horario en el auditorio"""
        # Buscar proyecciones del mismo auditorio y fecha
        existing_screenings = await self.repository.search(
            auditorium_id=screening_data.scr_aud_id,
            screening_date=screening_data.scr_date
        )
        
        # Verificar solapamiento de horarios (asumiendo 3 horas por función incluido limpieza)
        new_start = datetime.combine(screening_data.scr_date, screening_data.scr_time)
        new_end = new_start + timedelta(hours=3)
        
        for existing in existing_screenings:
            # Excluir la proyección actual si es una actualización
            if exclude_screening_id and existing.get('scr_id') == exclude_screening_id:
                continue
                
            if existing.get('scr_status') in ['scheduled', 'ongoing']:
                # Convertir scr_time a time si es timedelta
                existing_time = existing['scr_time']
                if isinstance(existing_time, timedelta):
                    # Convertir timedelta a time
                    total_seconds = int(existing_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    existing_time = time(hours, minutes, seconds)
                
                existing_start = datetime.combine(existing['scr_date'], existing_time)
                existing_end = existing_start + timedelta(hours=3)
                
                if (new_start < existing_end and new_end > existing_start):
                    raise HTTPException(
                        status_code=400, 
                        detail="Ya existe una proyección en ese horario en el auditorio"
                    )
    
    def _dict_to_screening_response(self, screening_dict: Dict[str, Any]) -> ScreeningResponse:
        """Convertir diccionario a modelo ScreeningResponse"""
        # Crear una copia del diccionario para modificar
        processed_dict = screening_dict.copy()
        
        # Convertir timedelta a time si es necesario
        if 'scr_time' in processed_dict and hasattr(processed_dict['scr_time'], 'total_seconds'):
            # Convertir timedelta a time
            total_seconds = int(processed_dict['scr_time'].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            processed_dict['scr_time'] = time(hours, minutes, seconds)
        
        # Convertir Decimal a float si es necesario
        if 'scr_price' in processed_dict and hasattr(processed_dict['scr_price'], '__float__'):
            processed_dict['scr_price'] = float(processed_dict['scr_price'])
        
        return ScreeningResponse(**processed_dict)
    
    def _dict_to_screening_summary(self, screening_dict: Dict[str, Any]) -> ScreeningSummary:
        """Convertir diccionario a modelo ScreeningSummary"""
        # Crear una copia del diccionario para modificar
        processed_dict = screening_dict.copy()
        
        # Convertir timedelta a time si es necesario
        if 'scr_time' in processed_dict and hasattr(processed_dict['scr_time'], 'total_seconds'):
            # Convertir timedelta a time
            total_seconds = int(processed_dict['scr_time'].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            processed_dict['scr_time'] = time(hours, minutes, seconds)
        
        # Convertir Decimal a float si es necesario
        if 'scr_price' in processed_dict and hasattr(processed_dict['scr_price'], '__float__'):
            processed_dict['scr_price'] = float(processed_dict['scr_price'])
        
        return ScreeningSummary(**processed_dict)

# Instancia global del service
screening_service = ScreeningService()
