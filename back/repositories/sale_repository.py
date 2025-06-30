from typing import List, Optional, Dict, Any
from models.sale import Sale
from db_connection import database

class SaleRepository:
    def __init__(self):
        self.db = database

    def create(self, sale_data: Dict[str, Any]) -> Sale:
        """Crear una nueva venta"""
        query = """
        INSERT INTO tb_sale 
        (sal_usr_id, sal_emp_id, sal_tic_id, sal_total_amount, sal_payment_method, sal_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            sale_data['sal_usr_id'],
            sale_data['sal_emp_id'],
            sale_data['sal_tic_id'],
            sale_data['sal_total_amount'],
            sale_data['sal_payment_method'],
            sale_data.get('sal_status', 'pending')
        )
        
        sale_id = self.db.execute_with_return(query, params)
        
        if sale_id:
            return self.get_by_id(sale_id)
        return None

    def get_by_id(self, sale_id: str) -> Optional[Sale]:
        """Obtener venta por ID"""
        query = "SELECT * FROM tb_sale WHERE sal_id = %s"
        result = self.db.execute_safe(query, (sale_id,))
        
        if result:
            return Sale(**result[0])
        return None

    def get_all(self) -> List[Sale]:
        """Obtener todas las ventas"""
        query = "SELECT * FROM tb_sale ORDER BY sal_created DESC"
        results = self.db.execute_safe(query)
        
        return [Sale(**row) for row in results]

    def get_by_user(self, user_id: str) -> List[Sale]:
        """Obtener ventas por usuario"""
        query = "SELECT * FROM tb_sale WHERE sal_usr_id = %s ORDER BY sal_created DESC"
        results = self.db.execute_safe(query, (user_id,))
        
        return [Sale(**row) for row in results]

    def get_by_employee(self, employee_id: str) -> List[Sale]:
        """Obtener ventas por empleado"""
        query = "SELECT * FROM tb_sale WHERE sal_emp_id = %s ORDER BY sal_created DESC"
        results = self.db.execute_safe(query, (employee_id,))
        
        return [Sale(**row) for row in results]

    def get_by_ticket(self, ticket_id: str) -> Optional[Sale]:
        """Obtener venta por ticket"""
        query = "SELECT * FROM tb_sale WHERE sal_tic_id = %s"
        result = self.db.execute_safe(query, (ticket_id,))
        
        if result:
            return Sale(**result[0])
        return None

    def get_by_status(self, status: str) -> List[Sale]:
        """Obtener ventas por estado"""
        query = "SELECT * FROM tb_sale WHERE sal_status = %s ORDER BY sal_created DESC"
        results = self.db.execute_safe(query, (status,))
        
        return [Sale(**row) for row in results]

    def get_by_payment_method(self, payment_method: str) -> List[Sale]:
        """Obtener ventas por método de pago"""
        query = "SELECT * FROM tb_sale WHERE sal_payment_method = %s ORDER BY sal_created DESC"
        results = self.db.execute_safe(query, (payment_method,))
        
        return [Sale(**row) for row in results]

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Sale]:
        """Obtener ventas por rango de fechas"""
        query = """
        SELECT * FROM tb_sale 
        WHERE DATE(sal_created) BETWEEN %s AND %s 
        ORDER BY sal_created DESC
        """
        results = self.db.execute_safe(query, (start_date, end_date))
        
        return [Sale(**row) for row in results]

    def update(self, sale_id: str, sale_data: Dict[str, Any]) -> Optional[Sale]:
        """Actualizar venta"""
        # Construir query de actualización dinámicamente
        set_clauses = []
        params = []
        
        for key, value in sale_data.items():
            if value is not None:
                set_clauses.append(f"{key} = %s")
                params.append(value)
        
        if not set_clauses:
            return self.get_by_id(sale_id)
        
        # Agregar timestamp de actualización
        set_clauses.append("sal_updated = CURRENT_TIMESTAMP")
        params.append(sale_id)
        
        query = f"UPDATE tb_sale SET {', '.join(set_clauses)} WHERE sal_id = %s"
        
        success = self.db.execute_safe(query, tuple(params))
        
        if success:
            return self.get_by_id(sale_id)
        return None

    def delete(self, sale_id: str) -> bool:
        """Eliminar venta"""
        query = "DELETE FROM tb_sale WHERE sal_id = %s"
        return self.db.execute_safe(query, (sale_id,)) is not None

    def update_status(self, sale_id: str, status: str) -> bool:
        """Actualizar estado de la venta"""
        query = "UPDATE tb_sale SET sal_status = %s, sal_updated = CURRENT_TIMESTAMP WHERE sal_id = %s"
        return self.db.execute_safe(query, (status, sale_id)) is not None

    def complete_sale(self, sale_id: str) -> bool:
        """Completar venta"""
        return self.update_status(sale_id, 'completed')

    def cancel_sale(self, sale_id: str) -> bool:
        """Cancelar venta"""
        return self.update_status(sale_id, 'cancelled')

    def refund_sale(self, sale_id: str) -> bool:
        """Reembolsar venta"""
        return self.update_status(sale_id, 'refunded')

    def get_sales_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Obtener resumen de ventas"""
        where_clause = ""
        params = []
        
        if start_date and end_date:
            where_clause = "WHERE DATE(sal_created) BETWEEN %s AND %s"
            params = [start_date, end_date]
        
        query = f"""
        SELECT 
            COUNT(*) as total_sales,
            SUM(sal_total_amount) as total_revenue,
            AVG(sal_total_amount) as average_sale,
            COUNT(CASE WHEN sal_status = 'completed' THEN 1 END) as completed_sales,
            COUNT(CASE WHEN sal_status = 'cancelled' THEN 1 END) as cancelled_sales,
            COUNT(CASE WHEN sal_status = 'refunded' THEN 1 END) as refunded_sales
        FROM tb_sale 
        {where_clause}
        """
        
        result = self.db.execute_safe(query, tuple(params) if params else ())
        
        if result:
            return dict(result[0])
        return {}
