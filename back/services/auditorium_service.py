from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from models.auditorium import AuditoriumCreate, AuditoriumUpdate, AuditoriumResponse, AuditoriumSummary
from repositories.auditorium_repository import auditorium_repository
import logging

logger = logging.getLogger(__name__)

class AuditoriumService:
    """Service para lógica de negocio de auditorios"""
    
    def __init__(self):
        self.repository = auditorium_repository
    
    async def get_auditoriums(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Obtener lista de auditorios con paginación"""
        try:
            if skip < 0:
                raise HTTPException(status_code=400, detail="Skip debe ser >= 0")
            if limit <= 0 or limit > 100:
                raise HTTPException(status_code=400, detail="Limit debe estar entre 1 y 100")
            
            auditoriums = await self.repository.get_all(skip, limit)
            total = await self.repository.count_total()
            
            auditorium_list = [self._dict_to_auditorium_summary(aud) for aud in auditoriums]
            
            return {
                "auditoriums": auditorium_list,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_auditoriums: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def get_auditorium_by_id(self, auditorium_id: str) -> AuditoriumResponse:
        """Obtener auditorio por ID"""
        try:
            if not auditorium_id or len(auditorium_id) < 30:
                raise HTTPException(status_code=400, detail="ID de auditorio inválido")
            
            auditorium = await self.repository.get_by_id(auditorium_id)
            if not auditorium:
                raise HTTPException(status_code=404, detail="Auditorio no encontrado")
            
            return self._dict_to_auditorium_response(auditorium)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_auditorium_by_id: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def create_auditorium(self, auditorium_data: AuditoriumCreate) -> AuditoriumResponse:
        """Crear nuevo auditorio"""
        try:
            # Validaciones de negocio
            await self._validate_auditorium_data(auditorium_data.dict())
            
            # Verificar nombre único
            existing = await self.repository.search_by_name(auditorium_data.aud_name)
            if any(aud['aud_name'].lower() == auditorium_data.aud_name.lower() for aud in existing):
                raise HTTPException(status_code=400, detail="Ya existe un auditorio con ese nombre")
            
            created_auditorium = await self.repository.create(auditorium_data.dict())
            
            if not created_auditorium:
                raise HTTPException(status_code=500, detail="Error creando auditorio")
            
            return self._dict_to_auditorium_response(created_auditorium)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in create_auditorium: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def update_auditorium(self, auditorium_id: str, auditorium_data: AuditoriumUpdate) -> AuditoriumResponse:
        """Actualizar auditorio existente"""
        try:
            if not auditorium_id:
                raise HTTPException(status_code=400, detail="ID de auditorio requerido")
            
            update_data = {k: v for k, v in auditorium_data.dict().items() if v is not None}
            
            if not update_data:
                raise HTTPException(status_code=400, detail="No hay datos para actualizar")
            
            await self._validate_auditorium_data(update_data, is_update=True)
            
            # Verificar nombre único si se está actualizando
            if 'aud_name' in update_data:
                existing = await self.repository.search_by_name(update_data['aud_name'])
                if any(aud['aud_name'].lower() == update_data['aud_name'].lower() 
                      and aud['aud_id'] != auditorium_id for aud in existing):
                    raise HTTPException(status_code=400, detail="Ya existe un auditorio con ese nombre")
            
            updated_auditorium = await self.repository.update(auditorium_id, update_data)
            
            if not updated_auditorium:
                raise HTTPException(status_code=404, detail="Auditorio no encontrado")
            
            return self._dict_to_auditorium_response(updated_auditorium)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in update_auditorium: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def delete_auditorium(self, auditorium_id: str) -> Dict[str, str]:
        """Eliminar auditorio"""
        try:
            if not auditorium_id:
                raise HTTPException(status_code=400, detail="ID de auditorio requerido")
            
            success = await self.repository.delete(auditorium_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Auditorio no encontrado")
            
            return {"message": "Auditorio eliminado exitosamente"}
        
        except HTTPException:
            raise
        except Exception as e:
            if "proyecciones asociadas" in str(e):
                raise HTTPException(status_code=409, detail=str(e))
            logger.error(f"Error in delete_auditorium: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def search_auditoriums(self, name: str) -> List[AuditoriumSummary]:
        """Buscar auditorios por nombre"""
        try:
            if not name or len(name.strip()) < 2:
                raise HTTPException(status_code=400, detail="El nombre debe tener al menos 2 caracteres")
            
            auditoriums = await self.repository.search_by_name(name.strip())
            return [self._dict_to_auditorium_summary(aud) for aud in auditoriums]
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in search_auditoriums: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    # Métodos auxiliares privados
    async def _validate_auditorium_data(self, data: Dict[str, Any], is_update: bool = False):
        """Validaciones de negocio adicionales"""
        # Validar capacidad razonable
        if 'aud_total_rows' in data and 'aud_seats_per_row' in data:
            total_capacity = data['aud_total_rows'] * data['aud_seats_per_row']
            if total_capacity > 500:
                raise HTTPException(
                    status_code=400, 
                    detail="La capacidad total no puede exceder 500 asientos"
                )
            if total_capacity < 10:
                raise HTTPException(
                    status_code=400, 
                    detail="La capacidad total debe ser de al menos 10 asientos"
                )
    
    def _dict_to_auditorium_response(self, auditorium_dict: Dict[str, Any]) -> AuditoriumResponse:
        """Convertir diccionario a modelo AuditoriumResponse"""
        return AuditoriumResponse(**auditorium_dict)
    
    def _dict_to_auditorium_summary(self, auditorium_dict: Dict[str, Any]) -> AuditoriumSummary:
        """Convertir diccionario a modelo AuditoriumSummary"""
        return AuditoriumSummary(**auditorium_dict)

# Instancia global del service
auditorium_service = AuditoriumService()
