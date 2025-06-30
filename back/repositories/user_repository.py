from typing import List, Optional, Dict, Any
from db_connection import database
import uuid
from datetime import datetime
import bcrypt

class UserRepository:
    """Repository para manejar operaciones de base de datos de usuarios"""
    
    def __init__(self):
        self.db = database
    
    def _hash_password(self, password: str) -> str:
        """Hash de contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verificar contraseña contra hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def get_all(self, skip: int = 0, limit: int = 100, status: str = None) -> List[Dict[str, Any]]:
        """Obtener todos los usuarios con paginación"""
        try:
            base_query = """
            SELECT usr_id, usr_name, usr_email, usr_phone, usr_birth_date, 
                   usr_status, usr_created, usr_updated
            FROM tb_user
            """
            
            if status:
                query = base_query + " WHERE usr_status = %s ORDER BY usr_created DESC LIMIT %s OFFSET %s"
                params = (status, limit, skip)
            else:
                query = base_query + " ORDER BY usr_created DESC LIMIT %s OFFSET %s"
                params = (limit, skip)
            
            result = self.db.execute_safe(query, params)
            return result
        except Exception as e:
            raise Exception(f"Error getting users: {str(e)}")
    
    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por ID (sin contraseña)"""
        try:
            query = """
            SELECT usr_id, usr_name, usr_email, usr_phone, usr_birth_date, 
                   usr_status, usr_created, usr_updated
            FROM tb_user 
            WHERE usr_id = %s
            """
            result = self.db.execute_safe(query, (user_id,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error getting user by ID: {str(e)}")
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por email (con contraseña para autenticación)"""
        try:
            query = """
            SELECT usr_id, usr_name, usr_email, usr_password_hash, usr_phone, 
                   usr_birth_date, usr_status, usr_created, usr_updated
            FROM tb_user 
            WHERE usr_email = %s
            """
            result = self.db.execute_safe(query, (email,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error getting user by email: {str(e)}")
    
    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo usuario"""
        try:
            user_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Hash de la contraseña
            hashed_password = self._hash_password(user_data['usr_password'])
            
            query = """
            INSERT INTO tb_user (usr_id, usr_name, usr_email, usr_password_hash, 
                               usr_phone, usr_birth_date, usr_status, usr_created, usr_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.db.execute_safe(query, (
                user_id,
                user_data['usr_name'],
                user_data['usr_email'],
                hashed_password,
                user_data.get('usr_phone'),
                user_data.get('usr_birth_date'),
                'active',
                now,
                now
            ))
            
            # Devolver el usuario creado (sin contraseña)
            return self.get_by_id(user_id)
            
        except Exception as e:
            if "Duplicate entry" in str(e) and "usr_email" in str(e):
                raise Exception("El email ya está registrado")
            raise Exception(f"Error creating user: {str(e)}")
    
    def update(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar usuario existente"""
        try:
            # Verificar que el usuario existe
            existing = self.get_by_id(user_id)
            if not existing:
                return None
            
            # Construir query dinámicamente
            set_clauses = []
            values = []
            
            for field, value in user_data.items():
                if field in ['usr_name', 'usr_email', 'usr_phone', 'usr_birth_date', 'usr_status']:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                return existing
            
            set_clauses.append("usr_updated = %s")
            values.append(datetime.now())
            values.append(user_id)
            
            query = f"""
            UPDATE tb_user 
            SET {', '.join(set_clauses)}
            WHERE usr_id = %s
            """
            
            self.db.execute_safe(query, tuple(values))
            return self.get_by_id(user_id)
            
        except Exception as e:
            if "Duplicate entry" in str(e) and "usr_email" in str(e):
                raise Exception("El email ya está registrado por otro usuario")
            raise Exception(f"Error updating user: {str(e)}")
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Cambiar contraseña de usuario"""
        try:
            # Obtener usuario con contraseña
            user = self.get_by_email_with_password(user_id)
            if not user:
                return False
            
            # Verificar contraseña actual
            if not self._verify_password(current_password, user['usr_password_hash']):
                raise Exception("Contraseña actual incorrecta")
            
            # Hash nueva contraseña
            new_hashed = self._hash_password(new_password)
            
            query = """
            UPDATE tb_user 
            SET usr_password_hash = %s, usr_updated = %s
            WHERE usr_id = %s
            """
            
            self.db.execute_safe(query, (new_hashed, datetime.now(), user_id))
            return True
            
        except Exception as e:
            raise Exception(f"Error changing password: {str(e)}")
    
    def get_by_email_with_password(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por ID incluyendo contraseña"""
        try:
            query = """
            SELECT usr_id, usr_name, usr_email, usr_password_hash, usr_phone, 
                   usr_birth_date, usr_status, usr_created, usr_updated
            FROM tb_user 
            WHERE usr_id = %s
            """
            result = self.db.execute_safe(query, (user_id,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error getting user with password: {str(e)}")
    
    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar usuario"""
        try:
            user = self.get_by_email(email)
            if not user:
                return None
            
            if user['usr_status'] != 'active':
                return None
            
            if not self._verify_password(password, user['usr_password_hash']):
                return None
            
            # Devolver usuario sin contraseña
            del user['usr_password_hash']
            return user
            
        except Exception as e:
            raise Exception(f"Error authenticating user: {str(e)}")
    
    def search(self, name: str = None, email: str = None) -> List[Dict[str, Any]]:
        """Buscar usuarios por criterios"""
        try:
            where_clauses = []
            values = []
            
            if name:
                where_clauses.append("usr_name LIKE %s")
                values.append(f"%{name}%")
            
            if email:
                where_clauses.append("usr_email LIKE %s")
                values.append(f"%{email}%")
            
            base_query = """
            SELECT usr_id, usr_name, usr_email, usr_phone, usr_birth_date, 
                   usr_status, usr_created, usr_updated
            FROM tb_user
            """
            
            if where_clauses:
                query = base_query + f" WHERE {' AND '.join(where_clauses)} ORDER BY usr_name"
            else:
                query = base_query + " ORDER BY usr_name"
            
            result = self.db.execute_safe(query, tuple(values))
            return result
            
        except Exception as e:
            raise Exception(f"Error searching users: {str(e)}")
    
    def count_total(self, status: str = None) -> int:
        """Contar total de usuarios"""
        try:
            if status:
                query = "SELECT COUNT(*) as total FROM tb_user WHERE usr_status = %s"
                result = self.db.execute_safe(query, (status,))
            else:
                query = "SELECT COUNT(*) as total FROM tb_user"
                result = self.db.execute_safe(query)
            
            return result[0]['total'] if result else 0
        except Exception as e:
            raise Exception(f"Error counting users: {str(e)}")

# Instancia global del repository
user_repository = UserRepository()
