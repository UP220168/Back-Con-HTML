from typing import List, Optional
from models.employee import Employee, EmployeeCreate, EmployeeUpdate
from repositories.employee_repository import EmployeeRepository
import bcrypt

class EmployeeService:
    def __init__(self):
        self.employee_repository = EmployeeRepository()
    
    def hash_password(self, password: str) -> str:
        """Encriptar contraseña"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_employee(self, employee_data: EmployeeCreate) -> Employee:
        """Crear un nuevo empleado"""
        # Verificar si el email ya existe
        existing_employee = self.employee_repository.get_by_email(employee_data.email)
        if existing_employee:
            raise ValueError("El email ya está registrado")
        
        # Encriptar contraseña
        hashed_password = self.hash_password(employee_data.password)
        
        # Crear empleado con contraseña encriptada
        employee_dict = employee_data.model_dump()
        employee_dict['password'] = hashed_password
        
        return self.employee_repository.create(employee_dict)
    
    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """Obtener empleado por ID"""
        return self.employee_repository.get_by_id(employee_id)
    
    def get_all_employees(self) -> List[Employee]:
        """Obtener todos los empleados"""
        return self.employee_repository.get_all()
    
    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Obtener empleado por email"""
        return self.employee_repository.get_by_email(email)
    
    def update_employee(self, employee_id: int, employee_data: EmployeeUpdate) -> Optional[Employee]:
        """Actualizar empleado"""
        # Verificar que el empleado existe
        existing_employee = self.employee_repository.get_by_id(employee_id)
        if not existing_employee:
            return None
        
        # Si se va a actualizar el email, verificar que no esté en uso
        if employee_data.email and employee_data.email != existing_employee.email:
            email_exists = self.employee_repository.get_by_email(employee_data.email)
            if email_exists:
                raise ValueError("El email ya está registrado")
        
        # Si se va a actualizar la contraseña, encriptarla
        employee_dict = employee_data.model_dump(exclude_unset=True)
        if 'password' in employee_dict:
            employee_dict['password'] = self.hash_password(employee_dict['password'])
        
        return self.employee_repository.update(employee_id, employee_dict)
    
    def delete_employee(self, employee_id: int) -> bool:
        """Eliminar empleado"""
        return self.employee_repository.delete(employee_id)
    
    def authenticate_employee(self, email: str, password: str) -> Optional[Employee]:
        """Autenticar empleado"""
        employee = self.employee_repository.get_by_email(email)
        if not employee:
            return None
        
        if not self.verify_password(password, employee.password):
            return None
        
        return employee
