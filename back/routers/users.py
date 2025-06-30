from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from models.user import UserCreate, UserUpdate, UserResponse, UserSummary, UserLogin, UserLoginResponse
from services.user_service import user_service

# Crear router
router = APIRouter(tags=["users"])

# GET /api/users/ - Listar usuarios
@router.get("/", response_model=dict)
async def get_users(
    skip: int = Query(0, ge=0, description="Elementos a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Límite de elementos")
):
    """
    Obtener lista de usuarios con paginación
    
    - **skip**: número de elementos a omitir (para paginación)
    - **limit**: número máximo de elementos a devolver (1-100)
    """
    return await user_service.get_users(skip=skip, limit=limit)

# GET /api/users/search - Buscar usuarios
@router.get("/search", response_model=List[UserSummary])
async def search_users(
    name: Optional[str] = Query(None, description="Buscar por nombre"),
    email: Optional[str] = Query(None, description="Buscar por email"),
    status: Optional[str] = Query(None, description="Buscar por estado")
):
    """
    Buscar usuarios por diferentes criterios
    """
    return await user_service.search_users(name=name, email=email, status=status)

# GET /api/users/{user_id} - Obtener usuario específico
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Obtener un usuario por su ID
    """
    return await user_service.get_user_by_id(user_id)

# POST /api/users/login - Autenticar usuario
@router.post("/login", response_model=UserLoginResponse)
async def login_user(login_data: UserLogin):
    """
    Autenticar usuario con email y contraseña
    """
    user = await user_service.authenticate_user(login_data.usr_email, login_data.usr_password)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Credenciales inválidas"
        )
    
    # Generar token simple (en producción usar JWT)
    access_token = f"token_{user.usr_id}"
    
    return UserLoginResponse(
        user=user,
        access_token=access_token,
        token_type="bearer"
    )

# POST /api/users/ - Crear nuevo usuario
@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """
    Crear un nuevo usuario
    """
    return await user_service.create_user(user)

# PUT /api/users/{user_id} - Actualizar usuario
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    """
    Actualizar un usuario existente
    """
    return await user_service.update_user(user_id, user_update)

# DELETE /api/users/{user_id} - Eliminar usuario (soft delete)
@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """
    Eliminar un usuario (cambiar estado a inactive)
    """
    return await user_service.delete_user(user_id)
