from typing import List, Optional, Dict, Any
from db_connection import database
import uuid
from datetime import datetime
import bcrypt

class EmployeeRepository:
    """Repository para manejar operaciones de base de datos de empleados"""
    
    def __init__(self):
        self.db = database
    
    def _hash_password(self, password: str) -> str:
        """Hash de contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verificar contraseña contra hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def get_all(self, skip: int = 0, limit: int = 100, position: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Obtener todos los empleados con paginación"""
        try:
            where_clauses = []
            values = []
            
            if position:
                where_clauses.append("emp_position = %s")
                values.append(position)
            
            if status:
                where_clauses.append("emp_status = %s")
                values.append(status)
            
            base_query = """
            SELECT emp_id, emp_name, emp_email, emp_position, emp_phone, 
                   emp_status, emp_created, emp_updated
            FROM tb_employee
            """
            
            if where_clauses:
                query = base_query + f" WHERE {' AND '.join(where_clauses)} ORDER BY emp_created DESC LIMIT %s OFFSET %s"
                values.extend([limit, skip])
            else:
                query = base_query + " ORDER BY emp_created DESC LIMIT %s OFFSET %s"
                values = [limit, skip]
            
            result = self.db.execute_safe(query, tuple(values))
            return result
        except Exception as e:
            raise Exception(f"Error getting employees: {str(e)}")
    
    def get_by_id(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Obtener empleado por ID (sin contraseña)"""
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
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtener empleado por email (con contraseña para autenticación)"""
        try:
            query = """
            SELECT emp_id, emp_name, emp_email, emp_position, emp_password_hash, 
                   emp_phone, emp_status, emp_created, emp_updated
            FROM tb_employee 
            WHERE emp_email = %s
            """
            result = self.db.execute_safe(query, (email,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error getting employee by email: {str(e)}")
    
    def create(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo empleado"""
        try:
            employee_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Hash de la contraseña
            hashed_password = self._hash_password(employee_data['emp_password'])
            
            query = """
            INSERT INTO tb_employee (emp_id, emp_name, emp_email, emp_position, 
                                   emp_password_hash, emp_phone, emp_status, emp_created, emp_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.db.execute_safe(query, (
                employee_id,
                employee_data['emp_name'],
                employee_data['emp_email'],
                employee_data['emp_position'],
                hashed_password,
                employee_data.get('emp_phone'),
                'active',
                now,
                now
            ))
            
            # Devolver el empleado creado (sin contraseña)
            return self.get_by_id(employee_id)
            
        except Exception as e:
            if "Duplicate entry" in str(e) and "emp_email" in str(e):
                raise Exception("El email ya está registrado")
            raise Exception(f"Error creating employee: {str(e)}")
    
    def update(self, employee_id: str, employee_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar empleado existente"""
        try:
            # Verificar que el empleado existe
            existing = self.get_by_id(employee_id)
            if not existing:
                return None
            
            # Construir query dinámicamente
            set_clauses = []
            values = []
            
            for field, value in employee_data.items():
                if field in ['emp_name', 'emp_email', 'emp_position', 'emp_phone', 'emp_status']:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                return existing
            
            set_clauses.append("emp_updated = %s")
            values.append(datetime.now())
            values.append(employee_id)
            
            query = f"""
            UPDATE tb_employee 
            SET {', '.join(set_clauses)}
            WHERE emp_id = %s
            """
            
            self.db.execute_safe(query, tuple(values))
            return self.get_by_id(employee_id)
            
        except Exception as e:
            if "Duplicate entry" in str(e) and "emp_email" in str(e):
                raise Exception("El email ya está registrado por otro empleado")
            raise Exception(f"Error updating employee: {str(e)}")
    
    def change_password(self, employee_id: str, current_password: str, new_password: str) -> bool:
        """Cambiar contraseña de empleado"""
        try:
            # Obtener empleado con contraseña
            employee = self.get_by_email_with_password(employee_id)
            if not employee:
                return False
            
            # Verificar contraseña actual
            if not self._verify_password(current_password, employee['emp_password_hash']):
                raise Exception("Contraseña actual incorrecta")
            
            # Hash nueva contraseña
            new_hashed = self._hash_password(new_password)
            
            query = """
            UPDATE tb_employee 
            SET emp_password_hash = %s, emp_updated = %s
            WHERE emp_id = %s
            """
            
            self.db.execute_safe(query, (new_hashed, datetime.now(), employee_id))
            return True
            
        except Exception as e:
            raise Exception(f"Error changing password: {str(e)}")
    
    def get_by_email_with_password(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Obtener empleado por ID incluyendo contraseña"""
        try:
            query = """
            SELECT emp_id, emp_name, emp_email, emp_position, emp_password_hash, 
                   emp_phone, emp_status, emp_created, emp_updated
            FROM tb_employee 
            WHERE emp_id = %s
            """
            result = self.db.execute_safe(query, (employee_id,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error getting employee with password: {str(e)}")
    
    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar empleado"""
        try:
            employee = self.get_by_email(email)
            if not employee:
                return None
            
            if employee['emp_status'] != 'active':
                return None
            
            if not self._verify_password(password, employee['emp_password_hash']):
                return None
            
            # Devolver empleado sin contraseña
            del employee['emp_password_hash']
            return employee
            
        except Exception as e:
            raise Exception(f"Error authenticating employee: {str(e)}")
    
    def search(self, name: str = None, email: str = None, position: str = None) -> List[Dict[str, Any]]:
        """Buscar empleados por criterios"""
        try:
            where_clauses = []
            values = []
            
            if name:
                where_clauses.append("emp_name LIKE %s")
                values.append(f"%{name}%")
            
            if email:
                where_clauses.append("emp_email LIKE %s")
                values.append(f"%{email}%")
            
            if position:
                where_clauses.append("emp_position = %s")
                values.append(position)
            
            base_query = """
            SELECT emp_id, emp_name, emp_email, emp_position, emp_phone, 
                   emp_status, emp_created, emp_updated
            FROM tb_employee
            """
            
            if where_clauses:
                query = base_query + f" WHERE {' AND '.join(where_clauses)} ORDER BY emp_name"
            else:
                query = base_query + " ORDER BY emp_name"
            
            result = self.db.execute_safe(query, tuple(values))
            return result
            
        except Exception as e:
            raise Exception(f"Error searching employees: {str(e)}")
    
    def count_total(self, position: str = None, status: str = None) -> int:
        """Contar total de empleados"""
        try:
            where_clauses = []
            values = []
            
            if position:
                where_clauses.append("emp_position = %s")
                values.append(position)
            
            if status:
                where_clauses.append("emp_status = %s")
                values.append(status)
            
            base_query = "SELECT COUNT(*) as total FROM tb_employee"
            
            if where_clauses:
                query = base_query + f" WHERE {' AND '.join(where_clauses)}"
            else:
                query = base_query
            
            result = self.db.execute_safe(query, tuple(values))
            return result[0]['total'] if result else 0
        except Exception as e:
            raise Exception(f"Error counting employees: {str(e)}")

# Instancia global del repository
employee_repository = EmployeeRepository()
