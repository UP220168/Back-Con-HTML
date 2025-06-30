from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from models.movie import MovieCreate, MovieUpdate, MovieResponse, MovieSummary, MovieStatus
from services.movie_service import movie_service

# Crear router
router = APIRouter()

# Datos simulados para probar (después conectarás con DB)
# Eliminados para usar service y repository reales

# GET /api/movies/ - Listar películas
@router.get("/", response_model=dict)
async def get_movies(
    skip: int = Query(0, ge=0, description="Elementos a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Límite de elementos")
):
    """
    Obtener lista de películas con paginación
    
    - **skip**: número de elementos a omitir (para paginación)
    - **limit**: número máximo de elementos a devolver (1-100)
    """
    return await movie_service.get_movies(skip=skip, limit=limit)

# GET /api/movies/search - Buscar películas
@router.get("/search", response_model=List[MovieSummary])
async def search_movies(
    title: Optional[str] = Query(None, description="Buscar por título"),
    genre: Optional[str] = Query(None, description="Buscar por género"),
    classification: Optional[str] = Query(None, description="Buscar por clasificación")
):
    """
    Buscar películas por diferentes criterios
    """
    return await movie_service.search_movies(title=title, genre=genre, classification=classification)

# GET /api/movies/{movie_id} - Obtener película específica
@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: str):
    """
    Obtener una película por su ID
    """
    return await movie_service.get_movie_by_id(movie_id)

# POST /api/movies/ - Crear nueva película
@router.post("/", response_model=MovieResponse, status_code=201)
async def create_movie(movie: MovieCreate):
    """
    Crear una nueva película
    """
    return await movie_service.create_movie(movie)

# PUT /api/movies/{movie_id} - Actualizar película
@router.put("/{movie_id}", response_model=MovieResponse)
async def update_movie(movie_id: str, movie_update: MovieUpdate):
    """
    Actualizar una película existente
    """
    return await movie_service.update_movie(movie_id, movie_update)

# DELETE /api/movies/{movie_id} - Eliminar película (soft delete)
@router.delete("/{movie_id}")
async def delete_movie(movie_id: str):
    """
    Eliminar una película (cambiar estado a inactive)
    """
    return await movie_service.delete_movie(movie_id)