from typing import List, Optional
from models.user import User, UserCreate, UserUpdate
from repositories.user_repository import UserRepository
import bcrypt

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    def hash_password(self, password: str) -> str:
        """Encriptar contraseña"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_user(self, user_data: UserCreate) -> User:
        """Crear un nuevo usuario"""
        # Verificar si el email ya existe
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("El email ya está registrado")
        
        # Encriptar contraseña
        hashed_password = self.hash_password(user_data.password)
        
        # Crear usuario con contraseña encriptada
        user_dict = user_data.model_dump()
        user_dict['password'] = hashed_password
        
        return self.user_repository.create(user_dict)
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        return self.user_repository.get_by_id(user_id)
    
    def get_all_users(self) -> List[User]:
        """Obtener todos los usuarios"""
        return self.user_repository.get_all()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return self.user_repository.get_by_email(email)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Actualizar usuario"""
        # Verificar que el usuario existe
        existing_user = self.user_repository.get_by_id(user_id)
        if not existing_user:
            return None
        
        # Si se va a actualizar el email, verificar que no esté en uso
        if user_data.email and user_data.email != existing_user.email:
            email_exists = self.user_repository.get_by_email(user_data.email)
            if email_exists:
                raise ValueError("El email ya está registrado")
        
        # Si se va a actualizar la contraseña, encriptarla
        user_dict = user_data.model_dump(exclude_unset=True)
        if 'password' in user_dict:
            user_dict['password'] = self.hash_password(user_dict['password'])
        
        return self.user_repository.update(user_id, user_dict)
    
    def delete_user(self, user_id: int) -> bool:
        """Eliminar usuario"""
        return self.user_repository.delete(user_id)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        
        if not self.verify_password(password, user.password):
            return None
        
        return user
