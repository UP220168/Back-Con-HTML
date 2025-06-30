from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

# Enums para validación
class EmployeePosition(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    MANAGER = "manager"

class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# Modelo base con campos comunes
class EmployeeBase(BaseModel):
    emp_name: str = Field(..., min_length=2, max_length=255, description="Nombre completo del empleado")
    emp_email: EmailStr = Field(..., description="Correo electrónico único")
    emp_position: EmployeePosition = Field(..., description="Posición del empleado")
    emp_phone: Optional[str] = Field(None, min_length=10, max_length=20, description="Número de teléfono")

# Para crear empleados (POST)
class EmployeeCreate(EmployeeBase):
    emp_password: str = Field(..., min_length=8, max_length=100, description="Contraseña (será hasheada)")

# Para actualizar empleados (PUT/PATCH)
class EmployeeUpdate(BaseModel):
    emp_name: Optional[str] = Field(None, min_length=2, max_length=255, description="Nombre completo")
    emp_email: Optional[EmailStr] = Field(None, description="Correo electrónico")
    emp_position: Optional[EmployeePosition] = Field(None, description="Posición del empleado")
    emp_phone: Optional[str] = Field(None, min_length=10, max_length=20, description="Teléfono")
    emp_status: Optional[EmployeeStatus] = Field(None, description="Estado del empleado")

# Para cambiar contraseña
class EmployeePasswordChange(BaseModel):
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, max_length=100, description="Nueva contraseña")

# Para respuestas completas (GET) - SIN contraseña
class EmployeeResponse(EmployeeBase):
    emp_id: str = Field(..., description="ID único del empleado")
    emp_status: EmployeeStatus = Field(..., description="Estado del empleado")
    emp_created: datetime = Field(..., description="Fecha de creación")
    emp_updated: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True

# Modelo principal que incluye todos los campos (usado internamente)
class Employee(EmployeeResponse):
    emp_password: str = Field(..., description="Contraseña hasheada (solo para uso interno)")

    class Config:
        from_attributes = True

# Para listas resumidas
class EmployeeSummary(BaseModel):
    emp_id: str = Field(..., description="ID único del empleado")
    emp_name: str = Field(..., description="Nombre del empleado")
    emp_email: EmailStr = Field(..., description="Email del empleado")
    emp_position: EmployeePosition = Field(..., description="Posición")
    emp_status: EmployeeStatus = Field(..., description="Estado del empleado")

    class Config:
        from_attributes = True

# Para login de empleados
class EmployeeLogin(BaseModel):
    emp_email: EmailStr = Field(..., description="Correo electrónico")
    emp_password: str = Field(..., description="Contraseña")

# Para respuesta de login de empleados
class EmployeeLoginResponse(BaseModel):
    employee: EmployeeResponse
    access_token: str = Field(..., description="Token de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
