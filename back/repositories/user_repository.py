from typing import List, Optional, Dict, Any
from db_connection import database
import uuid
from datetime import datetime

class UserRepository:
    """Repository para manejar operaciones de base de datos de usuarios"""
    
    def __init__(self):
        self.db = database
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener todos los usuarios con paginación"""
        try:
            query = """
            SELECT usr_id, usr_name, usr_email, usr_phone, usr_birth_date, 
                   usr_status, usr_created, usr_updated
            FROM tb_user 
            WHERE usr_status = 'active'
            ORDER BY usr_created DESC
            LIMIT %s OFFSET %s
            """
            result = self.db.execute_safe(query, (limit, skip))
            return result
        except Exception as e:
            raise Exception(f"Error getting users: {str(e)}")
    
    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por ID"""
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
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por email (incluye password para autenticación)"""
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
    
    async def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo usuario"""
        try:
            user_id = str(uuid.uuid4())
            now = datetime.now()
            
            query = """
            INSERT INTO tb_user (usr_id, usr_name, usr_email, usr_password_hash, 
                               usr_phone, usr_birth_date, usr_status, usr_created, usr_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                user_id,
                user_data.get('usr_name'),
                user_data.get('usr_email'),
                user_data.get('usr_password_hash'),  # Password ya debe estar hasheado
                user_data.get('usr_phone'),
                user_data.get('usr_birth_date'),
                user_data.get('usr_status', 'active'),
                now,
                now
            )
            
            self.db.execute_safe(query, values)
            
            # Retornar el usuario creado sin password
            return await self.get_by_id(user_id)
            
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")
    
    async def update(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar usuario existente"""
        try:
            # Campos que se pueden actualizar
            update_fields = []
            values = []
            
            if 'usr_name' in user_data:
                update_fields.append("usr_name = %s")
                values.append(user_data['usr_name'])
            
            if 'usr_email' in user_data:
                update_fields.append("usr_email = %s")
                values.append(user_data['usr_email'])
            
            if 'usr_phone' in user_data:
                update_fields.append("usr_phone = %s")
                values.append(user_data['usr_phone'])
            
            if 'usr_birth_date' in user_data:
                update_fields.append("usr_birth_date = %s")
                values.append(user_data['usr_birth_date'])
            
            if 'usr_status' in user_data:
                update_fields.append("usr_status = %s")
                values.append(user_data['usr_status'])
            
            if not update_fields:
                return await self.get_by_id(user_id)
            
            # Agregar timestamp de actualización
            update_fields.append("usr_updated = %s")
            values.append(datetime.now())
            
            # Agregar user_id al final para WHERE
            values.append(user_id)
            
            query = f"""
            UPDATE tb_user 
            SET {', '.join(update_fields)}
            WHERE usr_id = %s
            """
            
            result = self.db.execute_safe(query, tuple(values))
            
            if result:
                return await self.get_by_id(user_id)
            return None
            
        except Exception as e:
            raise Exception(f"Error updating user: {str(e)}")
    
    async def update_password(self, user_id: str, new_password_hash: str) -> bool:
        """Actualizar contraseña de usuario"""
        try:
            query = """
            UPDATE tb_user 
            SET usr_password_hash = %s, usr_updated = %s
            WHERE usr_id = %s
            """
            
            result = self.db.execute_safe(query, (new_password_hash, datetime.now(), user_id))
            return bool(result)
            
        except Exception as e:
            raise Exception(f"Error updating password: {str(e)}")
    
    async def delete(self, user_id: str) -> bool:
        """Eliminar usuario (soft delete)"""
        try:
            query = """
            UPDATE tb_user 
            SET usr_status = 'inactive', usr_updated = %s
            WHERE usr_id = %s
            """
            
            result = self.db.execute_safe(query, (datetime.now(), user_id))
            return bool(result)
            
        except Exception as e:
            raise Exception(f"Error deleting user: {str(e)}")
    
    async def search(self, name: Optional[str] = None, email: Optional[str] = None, 
                    status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Buscar usuarios por diferentes criterios"""
        try:
            where_clauses = []
            values = []
            
            if name:
                where_clauses.append("usr_name LIKE %s")
                values.append(f"%{name}%")
            
            if email:
                where_clauses.append("usr_email LIKE %s")
                values.append(f"%{email}%")
            
            if status:
                where_clauses.append("usr_status = %s")
                values.append(status)
            else:
                # Por defecto, solo mostrar usuarios activos
                where_clauses.append("usr_status = 'active'")
            
            if not where_clauses:
                where_clauses.append("usr_status = 'active'")
            
            query = f"""
            SELECT usr_id, usr_name, usr_email, usr_phone, usr_birth_date, 
                   usr_status, usr_created, usr_updated
            FROM tb_user 
            WHERE {' AND '.join(where_clauses)}
            ORDER BY usr_created DESC
            """
            
            result = self.db.execute_safe(query, tuple(values))
            return result
            
        except Exception as e:
            raise Exception(f"Error searching users: {str(e)}")
    
    async def count_total(self) -> int:
        """Contar total de usuarios activos"""
        try:
            query = "SELECT COUNT(*) as total FROM tb_user WHERE usr_status = 'active'"
            result = self.db.execute_safe(query)
            return result[0]['total'] if result else 0
        except Exception as e:
            raise Exception(f"Error counting users: {str(e)}")

    async def email_exists(self, email: str, exclude_user_id: Optional[str] = None) -> bool:
        """Verificar si un email ya existe en la base de datos"""
        try:
            query = "SELECT COUNT(*) as count FROM tb_user WHERE usr_email = %s"
            values = [email]
            
            if exclude_user_id:
                query += " AND usr_id != %s"
                values.append(exclude_user_id)
            
            result = self.db.execute_safe(query, tuple(values))
            return result[0]['count'] > 0 if result else False
        except Exception as e:
            raise Exception(f"Error checking email existence: {str(e)}")

# Instancia global del repository
user_repository = UserRepository()
