from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date
from enum import Enum

# Enums para validación
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# Modelo base con campos comunes
class UserBase(BaseModel):
    usr_name: str = Field(..., min_length=2, max_length=255, description="Nombre completo del usuario")
    usr_email: EmailStr = Field(..., description="Correo electrónico único")
    usr_phone: Optional[str] = Field(None, min_length=10, max_length=20, description="Número de teléfono")
    usr_birth_date: Optional[date] = Field(None, description="Fecha de nacimiento")

# Para crear usuarios (POST)
class UserCreate(UserBase):
    usr_password: str = Field(..., min_length=8, max_length=100, description="Contraseña (será hasheada)")

# Para actualizar usuarios (PUT/PATCH)
class UserUpdate(BaseModel):
    usr_name: Optional[str] = Field(None, min_length=2, max_length=255, description="Nombre completo")
    usr_email: Optional[EmailStr] = Field(None, description="Correo electrónico")
    usr_phone: Optional[str] = Field(None, min_length=10, max_length=20, description="Teléfono")
    usr_birth_date: Optional[date] = Field(None, description="Fecha de nacimiento")
    usr_status: Optional[UserStatus] = Field(None, description="Estado del usuario")

# Para cambiar contraseña
class UserPasswordChange(BaseModel):
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, max_length=100, description="Nueva contraseña")

# Para respuestas completas (GET) - SIN contraseña
class UserResponse(UserBase):
    usr_id: str = Field(..., description="ID único del usuario")
    usr_status: UserStatus = Field(..., description="Estado del usuario")
    usr_created: datetime = Field(..., description="Fecha de creación")
    usr_updated: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True

# Modelo principal que incluye todos los campos (usado internamente)
class User(UserResponse):
    usr_password: str = Field(..., description="Contraseña hasheada (solo para uso interno)")

    class Config:
        from_attributes = True

# Para listas resumidas
class UserSummary(BaseModel):
    usr_id: str = Field(..., description="ID único del usuario")
    usr_name: str = Field(..., description="Nombre del usuario")
    usr_email: EmailStr = Field(..., description="Email del usuario")
    usr_status: UserStatus = Field(..., description="Estado del usuario")

    class Config:
        from_attributes = True

# Para login
class UserLogin(BaseModel):
    usr_email: EmailStr = Field(..., description="Correo electrónico")
    usr_password: str = Field(..., description="Contraseña")

# Para respuesta de login
class UserLoginResponse(BaseModel):
    user: UserResponse
    access_token: str = Field(..., description="Token de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
