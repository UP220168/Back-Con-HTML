from typing import List, Optional, Dict, Any
from models.sale import Sale, SaleCreate, SaleUpdate
from repositories.sale_repository import SaleRepository
from repositories.user_repository import UserRepository
from repositories.employee_repository import EmployeeRepository
from repositories.ticket_repository import TicketRepository
from datetime import datetime

class SaleService:
    def __init__(self):
        self.sale_repository = SaleRepository()
        self.user_repository = UserRepository()
        self.employee_repository = EmployeeRepository()
        self.ticket_repository = TicketRepository()
    
    def create_sale(self, sale_data: SaleCreate) -> Sale:
        """Crear una nueva venta"""
        # Verificar que el usuario existe
        user = self.user_repository.get_by_id(sale_data.sal_usr_id)
        if not user:
            raise ValueError("El usuario especificado no existe")
        
        # Verificar que el empleado existe
        employee = self.employee_repository.get_by_id(sale_data.sal_emp_id)
        if not employee:
            raise ValueError("El empleado especificado no existe")
        
        # Verificar que el ticket existe y está disponible
        ticket = self.ticket_repository.get_by_id(sale_data.sal_tic_id)
        if not ticket:
            raise ValueError("El ticket especificado no existe")
        
        if ticket.tic_status not in ['available', 'reserved']:
            raise ValueError("El ticket no está disponible para venta")
        
        # Verificar que el ticket no ya esté vendido
        existing_sale = self.sale_repository.get_by_ticket(sale_data.sal_tic_id)
        if existing_sale and existing_sale.sal_status in ['completed', 'pending']:
            raise ValueError("El ticket ya ha sido vendido")
        
        # Crear la venta
        sale_dict = sale_data.model_dump()
        sale = self.sale_repository.create(sale_dict)
        
        # Si se crea exitosamente, marcar el ticket como vendido
        if sale:
            self.ticket_repository.sell_ticket(sale_data.sal_tic_id)
        
        return sale
    
    def get_sale(self, sale_id: str) -> Optional[Sale]:
        """Obtener venta por ID"""
        return self.sale_repository.get_by_id(sale_id)
    
    def get_all_sales(self) -> List[Sale]:
        """Obtener todas las ventas"""
        return self.sale_repository.get_all()
    
    def get_sales_by_user(self, user_id: str) -> List[Sale]:
        """Obtener ventas por usuario"""
        return self.sale_repository.get_by_user(user_id)
    
    def get_sales_by_employee(self, employee_id: str) -> List[Sale]:
        """Obtener ventas por empleado"""
        return self.sale_repository.get_by_employee(employee_id)
    
    def get_sale_by_ticket(self, ticket_id: str) -> Optional[Sale]:
        """Obtener venta por ticket"""
        return self.sale_repository.get_by_ticket(ticket_id)
    
    def get_sales_by_status(self, status: str) -> List[Sale]:
        """Obtener ventas por estado"""
        return self.sale_repository.get_by_status(status)
    
    def get_sales_by_payment_method(self, payment_method: str) -> List[Sale]:
        """Obtener ventas por método de pago"""
        return self.sale_repository.get_by_payment_method(payment_method)
    
    def get_sales_by_date_range(self, start_date: str, end_date: str) -> List[Sale]:
        """Obtener ventas por rango de fechas"""
        return self.sale_repository.get_by_date_range(start_date, end_date)
    
    def update_sale(self, sale_id: str, sale_data: SaleUpdate) -> Optional[Sale]:
        """Actualizar venta"""
        # Verificar que la venta existe
        existing_sale = self.sale_repository.get_by_id(sale_id)
        if not existing_sale:
            return None
        
        # Validar referencias si se están actualizando
        sale_dict = sale_data.model_dump(exclude_unset=True)
        
        if 'sal_usr_id' in sale_dict:
            user = self.user_repository.get_by_id(sale_dict['sal_usr_id'])
            if not user:
                raise ValueError("El usuario especificado no existe")
        
        if 'sal_emp_id' in sale_dict:
            employee = self.employee_repository.get_by_id(sale_dict['sal_emp_id'])
            if not employee:
                raise ValueError("El empleado especificado no existe")
        
        if 'sal_tic_id' in sale_dict:
            ticket = self.ticket_repository.get_by_id(sale_dict['sal_tic_id'])
            if not ticket:
                raise ValueError("El ticket especificado no existe")
        
        return self.sale_repository.update(sale_id, sale_dict)
    
    def delete_sale(self, sale_id: str) -> bool:
        """Eliminar venta"""
        # Obtener la venta antes de eliminarla para liberar el ticket
        sale = self.sale_repository.get_by_id(sale_id)
        if sale:
            # Liberar el ticket si la venta se elimina
            self.ticket_repository.release_ticket(sale.sal_tic_id)
        
        return self.sale_repository.delete(sale_id)
    
    def complete_sale(self, sale_id: str) -> bool:
        """Completar venta"""
        # Verificar que la venta existe y está pendiente
        sale = self.sale_repository.get_by_id(sale_id)
        if not sale:
            raise ValueError("La venta no existe")
        
        if sale.sal_status != 'pending':
            raise ValueError("Solo se pueden completar ventas pendientes")
        
        return self.sale_repository.complete_sale(sale_id)
    
    def cancel_sale(self, sale_id: str) -> bool:
        """Cancelar venta"""
        # Verificar que la venta existe
        sale = self.sale_repository.get_by_id(sale_id)
        if not sale:
            raise ValueError("La venta no existe")
        
        if sale.sal_status in ['cancelled', 'refunded']:
            raise ValueError("La venta ya está cancelada o reembolsada")
        
        # Liberar el ticket
        self.ticket_repository.release_ticket(sale.sal_tic_id)
        
        return self.sale_repository.cancel_sale(sale_id)
    
    def refund_sale(self, sale_id: str) -> bool:
        """Reembolsar venta"""
        # Verificar que la venta existe y está completada
        sale = self.sale_repository.get_by_id(sale_id)
        if not sale:
            raise ValueError("La venta no existe")
        
        if sale.sal_status != 'completed':
            raise ValueError("Solo se pueden reembolsar ventas completadas")
        
        # Liberar el ticket
        self.ticket_repository.release_ticket(sale.sal_tic_id)
        
        return self.sale_repository.refund_sale(sale_id)
    
    def get_sales_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Obtener resumen de ventas"""
        return self.sale_repository.get_sales_summary(start_date, end_date)
    
    def get_daily_sales(self, date: str = None) -> List[Sale]:
        """Obtener ventas del día"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        return self.get_sales_by_date_range(date, date)
