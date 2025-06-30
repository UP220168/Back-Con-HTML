from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from models.auditorium import AuditoriumCreate, AuditoriumUpdate, AuditoriumResponse, AuditoriumSummary
from services.auditorium_service import auditorium_service

# Crear router
router = APIRouter()

# GET /api/auditoriums/ - Listar auditorios
@router.get("/", response_model=dict)
async def get_auditoriums(
    skip: int = Query(0, ge=0, description="Elementos a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Límite de elementos")
):
    """
    Obtener lista de auditorios con paginación
    
    - **skip**: número de elementos a omitir (para paginación)
    - **limit**: número máximo de elementos a devolver (1-100)
    """
    return await auditorium_service.get_auditoriums(skip=skip, limit=limit)

# GET /api/auditoriums/search - Buscar auditorios
@router.get("/search", response_model=List[AuditoriumSummary])
async def search_auditoriums(
    name: str = Query(..., min_length=2, description="Buscar por nombre")
):
    """
    Buscar auditorios por nombre
    
    - **name**: buscar auditorios que contengan este texto en el nombre
    """
    return await auditorium_service.search_auditoriums(name=name)

# GET /api/auditoriums/{auditorium_id} - Obtener auditorio por ID
@router.get("/{auditorium_id}", response_model=AuditoriumResponse)
async def get_auditorium(
    auditorium_id: str = Path(..., description="ID único del auditorio")
):
    """
    Obtener un auditorio específico por su ID
    
    - **auditorium_id**: identificador único del auditorio
    """
    return await auditorium_service.get_auditorium_by_id(auditorium_id)

# POST /api/auditoriums/ - Crear nuevo auditorio
@router.post("/", response_model=AuditoriumResponse, status_code=201)
async def create_auditorium(auditorium: AuditoriumCreate):
    """
    Crear un nuevo auditorio
    
    - **auditorium**: datos del auditorio a crear
    """
    return await auditorium_service.create_auditorium(auditorium)

# PUT /api/auditoriums/{auditorium_id} - Actualizar auditorio
@router.put("/{auditorium_id}", response_model=AuditoriumResponse)
async def update_auditorium(
    auditorium_id: str = Path(..., description="ID único del auditorio"),
    auditorium: AuditoriumUpdate = ...
):
    """
    Actualizar un auditorio existente
    
    - **auditorium_id**: identificador único del auditorio
    - **auditorium**: datos actualizados del auditorio
    """
    return await auditorium_service.update_auditorium(auditorium_id, auditorium)

# DELETE /api/auditoriums/{auditorium_id} - Eliminar auditorio
@router.delete("/{auditorium_id}")
async def delete_auditorium(
    auditorium_id: str = Path(..., description="ID único del auditorio")
):
    """
    Eliminar un auditorio
    
    - **auditorium_id**: identificador único del auditorio a eliminar
    """
    return await auditorium_service.delete_auditorium(auditorium_id)
