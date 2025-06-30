from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from models.user import UserCreate, UserUpdate, UserResponse, UserSummary
from repositories.user_repository import user_repository
import logging
import bcrypt
from datetime import datetime, date

logger = logging.getLogger(__name__)

class UserService:
    """Service para lógica de negocio de usuarios"""
    
    def __init__(self):
        self.repository = user_repository
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Obtener lista de usuarios con paginación"""
        try:
            # Validar parámetros
            if skip < 0:
                raise HTTPException(status_code=400, detail="Skip debe ser >= 0")
            if limit <= 0 or limit > 100:
                raise HTTPException(status_code=400, detail="Limit debe estar entre 1 y 100")
            
            # Obtener usuarios y total
            users = await self.repository.get_all(skip, limit)
            total = await self.repository.count_total()
            
            # Convertir a modelos Pydantic
            user_list = [self._dict_to_user_summary(user) for user in users]
            
            return {
                "users": user_list,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_users: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """Obtener usuario por ID"""
        try:
            # Validar formato UUID (básico)
            if not user_id or len(user_id) < 30:
                raise HTTPException(status_code=400, detail="ID de usuario inválido")
            
            user = await self.repository.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            return self._dict_to_user_response(user)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_user_by_id: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Crear nuevo usuario"""
        try:
            # Validaciones de negocio adicionales
            await self._validate_user_data(user_data.dict())
            
            # Verificar que el email no existe
            if await self.repository.email_exists(user_data.usr_email):
                raise HTTPException(status_code=400, detail="El email ya está registrado")
            
            # Hashear password
            password_hash = self._hash_password(user_data.usr_password)
            
            # Preparar datos para crear
            create_data = user_data.dict()
            create_data['usr_password_hash'] = password_hash
            del create_data['usr_password']  # Remover password en texto plano
            
            # Crear usuario
            created_user = await self.repository.create(create_data)
            
            if not created_user:
                raise HTTPException(status_code=500, detail="Error creando usuario")
            
            return self._dict_to_user_response(created_user)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in create_user: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """Actualizar usuario existente"""
        try:
            # Validar ID
            if not user_id:
                raise HTTPException(status_code=400, detail="ID de usuario requerido")
            
            # Solo incluir campos que no son None
            update_data = {k: v for k, v in user_data.dict().items() if v is not None}
            
            if not update_data:
                raise HTTPException(status_code=400, detail="No hay datos para actualizar")
            
            # Validaciones de negocio
            await self._validate_user_data(update_data, is_update=True)
            
            # Verificar email único si se está actualizando
            if 'usr_email' in update_data:
                if await self.repository.email_exists(update_data['usr_email'], user_id):
                    raise HTTPException(status_code=400, detail="El email ya está registrado")
            
            # Hashear password si se está actualizando
            if 'usr_password' in update_data:
                update_data['usr_password_hash'] = self._hash_password(update_data['usr_password'])
                del update_data['usr_password']
            
            # Actualizar
            updated_user = await self.repository.update(user_id, update_data)
            
            if not updated_user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            return self._dict_to_user_response(updated_user)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in update_user: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def delete_user(self, user_id: str) -> Dict[str, str]:
        """Eliminar usuario (soft delete)"""
        try:
            if not user_id:
                raise HTTPException(status_code=400, detail="ID de usuario requerido")
            
            success = await self.repository.delete(user_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            return {"message": "Usuario eliminado exitosamente"}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in delete_user: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def search_users(self, name: str = None, email: str = None, phone: str = None) -> List[UserSummary]:
        """Buscar usuarios por criterios"""
        try:
            if not any([name, email, phone]):
                raise HTTPException(status_code=400, detail="Debe proporcionar al menos un criterio de búsqueda")
            
            users = await self.repository.search(name, email, phone)
            
            return [self._dict_to_user_summary(user) for user in users]
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in search_users: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        """Autenticar usuario por email y password"""
        try:
            user = await self.repository.get_by_email(email)
            if not user:
                return None
            
            if user['usr_status'] != 'active':
                return None
            
            # Verificar password
            if not self._verify_password(password, user['usr_password_hash']):
                return None
            
            # Remover password hash del resultado
            user_dict = {k: v for k, v in user.items() if k != 'usr_password_hash'}
            return self._dict_to_user_response(user_dict)
        
        except Exception as e:
            logger.error(f"Error in authenticate_user: {str(e)}")
            return None
    
    # Métodos auxiliares privados
    async def _validate_user_data(self, data: Dict[str, Any], is_update: bool = False):
        """Validaciones de negocio adicionales"""
        # Validar edad mínima
        if 'usr_birth_date' in data and data['usr_birth_date']:
            birth_date = data['usr_birth_date']
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 13:
                raise HTTPException(
                    status_code=400, 
                    detail="El usuario debe tener al menos 13 años"
                )
        
        # Validar formato básico de email
        if 'usr_email' in data:
            email = data['usr_email']
            if '@' not in email or '.' not in email:
                raise HTTPException(
                    status_code=400, 
                    detail="Formato de email inválido"
                )
        
        # Validar password mínimo (solo en creación o si se proporciona)
        if 'usr_password' in data:
            password = data['usr_password']
            if len(password) < 6:
                raise HTTPException(
                    status_code=400, 
                    detail="La contraseña debe tener al menos 6 caracteres"
                )
    
    def _hash_password(self, password: str) -> str:
        """Hashear password usando bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verificar password contra hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _dict_to_user_response(self, user_dict: Dict[str, Any]) -> UserResponse:
        """Convertir diccionario a modelo UserResponse"""
        return UserResponse(**user_dict)
    
    def _dict_to_user_summary(self, user_dict: Dict[str, Any]) -> UserSummary:
        """Convertir diccionario a modelo UserSummary"""
        return UserSummary(**user_dict)

# Instancia global del service
user_service = UserService()
