from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from datetime import date
from models.screening import ScreeningCreate, ScreeningUpdate, ScreeningResponse, ScreeningSummary
from services.screening_service import screening_service

# Crear router
router = APIRouter(tags=["screenings"])

# GET /api/screenings/ - Listar proyecciones
@router.get("/", response_model=dict)
async def get_screenings(
    skip: int = Query(0, ge=0, description="Elementos a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Límite de elementos")
):
    """
    Obtener lista de proyecciones con paginación
    
    - **skip**: número de elementos a omitir (para paginación)
    - **limit**: número máximo de elementos a devolver (1-100)
    """
    return await screening_service.get_screenings(skip=skip, limit=limit)

# GET /api/screenings/search - Buscar proyecciones
@router.get("/search", response_model=List[ScreeningSummary])
async def search_screenings(
    movie_id: Optional[str] = Query(None, description="Buscar por película"),
    auditorium_id: Optional[str] = Query(None, description="Buscar por auditorio"),
    screening_date: Optional[date] = Query(None, description="Buscar por fecha"),
    status: Optional[str] = Query(None, description="Buscar por estado")
):
    """
    Buscar proyecciones por diferentes criterios
    """
    return await screening_service.search_screenings(movie_id=movie_id, auditorium_id=auditorium_id, 
                                                    screening_date=screening_date, status=status)

# GET /api/screenings/{screening_id} - Obtener proyección específica
@router.get("/{screening_id}", response_model=ScreeningResponse)
async def get_screening(screening_id: str):
    """
    Obtener una proyección por su ID
    """
    return await screening_service.get_screening_by_id(screening_id)

# POST /api/screenings/ - Crear nueva proyección
@router.post("/", response_model=ScreeningResponse, status_code=201)
async def create_screening(screening: ScreeningCreate):
    """
    Crear una nueva proyección
    """
    return await screening_service.create_screening(screening)

# PUT /api/screenings/{screening_id} - Actualizar proyección
@router.put("/{screening_id}", response_model=ScreeningResponse)
async def update_screening(screening_id: str, screening_update: ScreeningUpdate):
    """
    Actualizar una proyección existente
    """
    return await screening_service.update_screening(screening_id, screening_update)

# DELETE /api/screenings/{screening_id} - Eliminar proyección (soft delete)
@router.delete("/{screening_id}")
async def delete_screening(screening_id: str):
    """
    Eliminar una proyección (cambiar estado a cancelled)
    """
    return await screening_service.delete_screening(screening_id)
