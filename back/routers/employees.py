from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from models.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeSummary, EmployeeLogin
from services.employee_service import employee_service

router = APIRouter(tags=["employees"])

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate):
    """Crear un nuevo empleado"""
    return await employee_service.create_employee(employee)

@router.get("/", response_model=Dict[str, Any])
async def get_employees(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número de registros a retornar"),
):
    """Obtener lista de empleados con paginación"""
    return await employee_service.get_employees(skip, limit)

@router.get("/search", response_model=List[EmployeeSummary])
async def search_employees(
    name: Optional[str] = Query(None, description="Buscar por nombre"),
    email: Optional[str] = Query(None, description="Buscar por email"),
    position: Optional[str] = Query(None, description="Buscar por posición"),
):
    """Buscar empleados por criterios"""
    return await employee_service.search_employees(name, email, position)

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str):
    """Obtener un empleado por ID"""
    return await employee_service.get_employee_by_id(employee_id)

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(employee_id: str, employee_data: EmployeeUpdate):
    """Actualizar un empleado"""
    return await employee_service.update_employee(employee_id, employee_data)

@router.delete("/{employee_id}")
async def delete_employee(employee_id: str):
    """Eliminar un empleado (soft delete)"""
    return await employee_service.delete_employee(employee_id)

@router.post("/authenticate", response_model=EmployeeResponse)
async def authenticate_employee(login_data: EmployeeLogin):
    """Autenticar un empleado"""
    return await employee_service.authenticate_employee(login_data.emp_email, login_data.emp_password)
