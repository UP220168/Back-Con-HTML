from typing import List, Optional, Dict, Any
from db_connection import database
import uuid
from datetime import datetime
import bcrypt

class EmployeeRepository:
    """Repository para manejar operaciones de base de datos de empleados"""
    
    def __init__(self):
        self.db = database
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener todos los empleados con paginación"""
        try:
            query = """
            SELECT emp_id, emp_name, emp_email, emp_position, emp_phone, 
                   emp_status, emp_created, emp_updated
            FROM tb_employee 
            WHERE emp_status = 'active'
            ORDER BY emp_created DESC
            LIMIT %s OFFSET %s
            """
            result = self.db.execute_safe(query, (limit, skip))
            return result
        except Exception as e:
            raise Exception(f"Error getting employees: {str(e)}")
    
    async def get_by_id(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Obtener empleado por ID"""
        try:
            query = """
            SELECT emp_id, emp_name, emp_email, emp_position, emp_phone, 
                   emp_status, emp_created, emp_updated
            FROM tb_employee 
            WHERE emp_id = %s
            """
            result = self.db.execute_safe(query, (employee_id,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error getting employee by ID: {str(e)}")
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtener empleado por email (incluye password hash para autenticación)"""
        try:
            query = """
            SELECT emp_id, emp_name, emp_email, emp_position, emp_password_hash, 
                   emp_phone, emp_status, emp_created, emp_updated
            FROM tb_employee 
            WHERE emp_email = %s
            """
            result = self.db.execute_safe(query, (email.lower(),))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error getting employee by email: {str(e)}")
    
    async def create(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo empleado"""
        try:
            employee_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Hash de la contraseña
            password_hash = self._hash_password(employee_data['emp_password'])
            
            query = """
            INSERT INTO tb_employee (emp_id, emp_name, emp_email, emp_position, 
                                   emp_password_hash, emp_phone, emp_status, emp_created, emp_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.db.execute_safe(query, (
                employee_id,
                employee_data['emp_name'],
                employee_data['emp_email'].lower(),
                employee_data['emp_position'],
                password_hash,
                employee_data.get('emp_phone'),
                'active',
                now,
                now
            ))
            
            # Devolver el empleado creado (sin el password hash)
            return await self.get_by_id(employee_id)
            
        except Exception as e:
            raise Exception(f"Error creating employee: {str(e)}")
    
    async def update(self, employee_id: str, employee_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar empleado existente"""
        try:
            # Verificar que el empleado existe
            existing = await self.get_by_id(employee_id)
            if not existing:
                return None
            
            # Construir query dinámicamente basado en campos proporcionados
            set_clauses = []
            values = []
            
            for field, value in employee_data.items():
                if field in ['emp_name', 'emp_email', 'emp_position', 'emp_phone', 'emp_status']:
                    set_clauses.append(f"{field} = %s")
                    # Convertir email a minúsculas si está presente
                    if field == 'emp_email':
                        value = value.lower()
                    values.append(value)
                elif field == 'emp_password':
                    # Hashear nueva contraseña
                    set_clauses.append("emp_password_hash = %s")
                    values.append(self._hash_password(value))
            
            if not set_clauses:
                return existing  # No hay nada que actualizar
            
            # Agregar timestamp de actualización
            set_clauses.append("emp_updated = %s")
            values.append(datetime.now())
            values.append(employee_id)  # Para el WHERE
            
            query = f"""
            UPDATE tb_employee 
            SET {', '.join(set_clauses)}
            WHERE emp_id = %s
            """
            
            self.db.execute_safe(query, tuple(values))
            
            # Devolver el empleado actualizado
            return await self.get_by_id(employee_id)
            
        except Exception as e:
            raise Exception(f"Error updating employee: {str(e)}")
    
    async def delete(self, employee_id: str) -> bool:
        """Eliminar empleado (soft delete)"""
        try:
            # Verificar que el empleado existe
            existing = await self.get_by_id(employee_id)
            if not existing:
                return False
            
            query = """
            UPDATE tb_employee 
            SET emp_status = 'inactive', emp_updated = %s
            WHERE emp_id = %s
            """
            
            self.db.execute_safe(query, (datetime.now(), employee_id))
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting employee: {str(e)}")
    
    async def search(self, name: str = None, email: str = None, position: str = None) -> List[Dict[str, Any]]:
        """Buscar empleados por criterios"""
        try:
            where_clauses = ["emp_status = 'active'"]
            values = []
            
            if name:
                where_clauses.append("emp_name LIKE %s")
                values.append(f"%{name}%")
            
            if email:
                where_clauses.append("emp_email LIKE %s")
                values.append(f"%{email.lower()}%")
            
            if position:
                where_clauses.append("emp_position = %s")
                values.append(position)
            
            query = f"""
            SELECT emp_id, emp_name, emp_email, emp_position, emp_phone, 
                   emp_status, emp_created, emp_updated
            FROM tb_employee 
            WHERE {' AND '.join(where_clauses)}
            ORDER BY emp_created DESC
            """
            
            result = self.db.execute_safe(query, tuple(values))
            return result
            
        except Exception as e:
            raise Exception(f"Error searching employees: {str(e)}")
    
    async def count_total(self) -> int:
        """Contar total de empleados activos"""
        try:
            query = "SELECT COUNT(*) as total FROM tb_employee WHERE emp_status = 'active'"
            result = self.db.execute_safe(query)
            return result[0]['total'] if result else 0
        except Exception as e:
            raise Exception(f"Error counting employees: {str(e)}")
    
    async def email_exists(self, email: str, exclude_employee_id: str = None) -> bool:
        """Verificar si un email ya existe (útil para validaciones)"""
        try:
            query = "SELECT emp_id FROM tb_employee WHERE emp_email = %s"
            values = [email.lower()]
            
            if exclude_employee_id:
                query += " AND emp_id != %s"
                values.append(exclude_employee_id)
            
            result = self.db.execute_safe(query, tuple(values))
            return len(result) > 0
        except Exception as e:
            raise Exception(f"Error checking email existence: {str(e)}")
    
    async def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar empleado por email y password"""
        try:
            employee = await self.get_by_email(email)
            if not employee:
                return None
            
            if employee['emp_status'] != 'active':
                return None
            
            # Verificar password
            if not self._verify_password(password, employee['emp_password_hash']):
                return None
            
            # Remover password hash del resultado
            employee_dict = {k: v for k, v in employee.items() if k != 'emp_password_hash'}
            return employee_dict
        
        except Exception as e:
            raise Exception(f"Error authenticating employee: {str(e)}")
    
    def _hash_password(self, password: str) -> str:
        """Hashear password usando bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verificar password contra hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Instancia global del repository
employee_repository = EmployeeRepository()
