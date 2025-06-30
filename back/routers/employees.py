from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from models.employee import Employee, EmployeeCreate, EmployeeUpdate, EmployeeResponse
from services.employee_service import EmployeeService

router = APIRouter(tags=["employees"])
employee_service = EmployeeService()

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate):
    """Crear un nuevo empleado"""
    try:
        created_employee = employee_service.create_employee(employee)
        return created_employee
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear empleado: {str(e)}"
        )

@router.get("/", response_model=List[EmployeeResponse])
def get_all_employees():
    """Obtener todos los empleados"""
    try:
        employees = employee_service.get_all_employees()
        return employees
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener empleados: {str(e)}"
        )

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str):
    """Obtener un empleado por ID"""
    try:
        employee = employee_service.get_employee(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado"
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener empleado: {str(e)}"
        )

@router.get("/email/{email}", response_model=EmployeeResponse)
def get_employee_by_email(email: str):
    """Obtener un empleado por email"""
    try:
        employee = employee_service.get_employee_by_email(email)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado"
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener empleado: {str(e)}"
        )

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: str, employee_data: EmployeeUpdate):
    """Actualizar un empleado"""
    try:
        updated_employee = employee_service.update_employee(employee_id, employee_data)
        if not updated_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado"
            )
        return updated_employee
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar empleado: {str(e)}"
        )

@router.delete("/{employee_id}")
def delete_employee(employee_id: str):
    """Eliminar un empleado"""
    try:
        success = employee_service.delete_employee(employee_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado"
            )
        return {"message": "Empleado eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar empleado: {str(e)}"
        )

@router.post("/authenticate")
def authenticate_employee(email: str, password: str):
    """Autenticar un empleado"""
    try:
        employee = employee_service.authenticate_employee(email, password)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al autenticar empleado: {str(e)}"
        )
