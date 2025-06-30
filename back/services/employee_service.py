from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from models.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeSummary
from repositories.employee_repository import employee_repository
import logging
import bcrypt

logger = logging.getLogger(__name__)

class EmployeeService:
    """Service para lógica de negocio de empleados"""
    
    def __init__(self):
        self.repository = employee_repository
    
    async def get_employees(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Obtener lista de empleados con paginación"""
        try:
            # Validar parámetros
            if skip < 0:
                raise HTTPException(status_code=400, detail="Skip debe ser >= 0")
            if limit <= 0 or limit > 100:
                raise HTTPException(status_code=400, detail="Limit debe estar entre 1 y 100")
            
            # Obtener empleados y total
            employees = await self.repository.get_all(skip, limit)
            total = await self.repository.count_total()
            
            # Convertir a modelos Pydantic
            employee_list = [self._dict_to_employee_summary(employee) for employee in employees]
            
            return {
                "employees": employee_list,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_employees: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def get_employee_by_id(self, employee_id: str) -> EmployeeResponse:
        """Obtener empleado por ID"""
        try:
            # Validar formato UUID (básico)
            if not employee_id or len(employee_id) < 30:
                raise HTTPException(status_code=400, detail="ID de empleado inválido")
            
            employee = await self.repository.get_by_id(employee_id)
            if not employee:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")
            
            return self._dict_to_employee_response(employee)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_employee_by_id: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def create_employee(self, employee_data: EmployeeCreate) -> EmployeeResponse:
        """Crear nuevo empleado"""
        try:
            # Validaciones de negocio adicionales
            await self._validate_employee_data(employee_data.dict())
            
            # Verificar que el email no existe
            if await self.repository.email_exists(employee_data.emp_email):
                raise HTTPException(status_code=400, detail="El email ya está registrado")
            
            # Preparar datos para crear
            create_data = employee_data.dict()
            
            # Crear empleado
            created_employee = await self.repository.create(create_data)
            
            if not created_employee:
                raise HTTPException(status_code=500, detail="Error creando empleado")
            
            return self._dict_to_employee_response(created_employee)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in create_employee: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def update_employee(self, employee_id: str, employee_data: EmployeeUpdate) -> EmployeeResponse:
        """Actualizar empleado existente"""
        try:
            # Validar ID
            if not employee_id:
                raise HTTPException(status_code=400, detail="ID de empleado requerido")
            
            # Solo incluir campos que no son None
            update_data = {k: v for k, v in employee_data.dict().items() if v is not None}
            
            if not update_data:
                raise HTTPException(status_code=400, detail="No hay datos para actualizar")
            
            # Validaciones de negocio
            await self._validate_employee_data(update_data, is_update=True)
            
            # Verificar email único si se está actualizando
            if 'emp_email' in update_data:
                if await self.repository.email_exists(update_data['emp_email'], employee_id):
                    raise HTTPException(status_code=400, detail="El email ya está registrado")
            
            # Actualizar
            updated_employee = await self.repository.update(employee_id, update_data)
            
            if not updated_employee:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")
            
            return self._dict_to_employee_response(updated_employee)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in update_employee: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def delete_employee(self, employee_id: str) -> Dict[str, str]:
        """Eliminar empleado (soft delete)"""
        try:
            if not employee_id:
                raise HTTPException(status_code=400, detail="ID de empleado requerido")
            
            success = await self.repository.delete(employee_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")
            
            return {"message": "Empleado eliminado exitosamente"}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in delete_employee: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def search_employees(self, name: str = None, email: str = None, position: str = None) -> List[EmployeeSummary]:
        """Buscar empleados por criterios"""
        try:
            if not any([name, email, position]):
                raise HTTPException(status_code=400, detail="Debe proporcionar al menos un criterio de búsqueda")
            
            employees = await self.repository.search(name, email, position)
            
            return [self._dict_to_employee_summary(employee) for employee in employees]
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in search_employees: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def authenticate_employee(self, email: str, password: str) -> EmployeeResponse:
        """Autenticar empleado por email y password"""
        try:
            employee = await self.repository.authenticate(email, password)
            if not employee:
                raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
            return self._dict_to_employee_response(employee)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in authenticate_employee: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    # Métodos auxiliares privados
    async def _validate_employee_data(self, data: Dict[str, Any], is_update: bool = False):
        """Validaciones de negocio adicionales"""
        # Validar formato básico de email
        if 'emp_email' in data:
            email = data['emp_email']
            if '@' not in email or '.' not in email:
                raise HTTPException(
                    status_code=400, 
                    detail="Formato de email inválido"
                )
        
        # Validar password mínimo (solo en creación o si se proporciona)
        if 'emp_password' in data:
            password = data['emp_password']
            if len(password) < 8:
                raise HTTPException(
                    status_code=400, 
                    detail="La contraseña debe tener al menos 8 caracteres"
                )
        
        # Validar posición válida
        if 'emp_position' in data:
            valid_positions = ['admin', 'employee', 'manager']
            if data['emp_position'] not in valid_positions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Posición inválida. Debe ser una de: {', '.join(valid_positions)}"
                )
    
    def _dict_to_employee_response(self, employee_dict: Dict[str, Any]) -> EmployeeResponse:
        """Convertir diccionario a modelo EmployeeResponse"""
        return EmployeeResponse(**employee_dict)
    
    def _dict_to_employee_summary(self, employee_dict: Dict[str, Any]) -> EmployeeSummary:
        """Convertir diccionario a modelo EmployeeSummary"""
        return EmployeeSummary(**employee_dict)

# Instancia global del service
employee_service = EmployeeService()
