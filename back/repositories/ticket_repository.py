from typing import List, Optional, Dict, Any
from models.ticket import Ticket
from db_connection import database

class TicketRepository:
    def __init__(self):
        self.db = database

    def create(self, ticket_data: Dict[str, Any]) -> Ticket:
        """Crear un nuevo ticket"""
        query = """
        INSERT INTO tb_ticket 
        (tic_row, tic_seat, tic_scr_id, tic_status)
        VALUES (%s, %s, %s, %s)
        """
        
        params = (
            ticket_data['tic_row'],
            ticket_data['tic_seat'],
            ticket_data['tic_scr_id'],
            ticket_data.get('tic_status', 'available')
        )
        
        ticket_id = self.db.execute_with_return(query, params)
        
        if ticket_id:
            return self.get_by_id(ticket_id)
        return None

    def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """Obtener ticket por ID"""
        query = "SELECT * FROM tb_ticket WHERE tic_id = %s"
        result = self.db.execute_safe(query, (ticket_id,))
        
        if result:
            return Ticket(**result[0])
        return None

    def get_all(self) -> List[Ticket]:
        """Obtener todos los tickets"""
        query = "SELECT * FROM tb_ticket ORDER BY tic_scr_id, tic_row, tic_seat"
        results = self.db.execute_safe(query)
        
        return [Ticket(**row) for row in results]

    def get_by_screening(self, screening_id: str) -> List[Ticket]:
        """Obtener tickets por proyección"""
        query = "SELECT * FROM tb_ticket WHERE tic_scr_id = %s ORDER BY tic_row, tic_seat"
        results = self.db.execute_safe(query, (screening_id,))
        
        return [Ticket(**row) for row in results]

    def get_by_screening_and_status(self, screening_id: str, status: str) -> List[Ticket]:
        """Obtener tickets por proyección y estado"""
        query = "SELECT * FROM tb_ticket WHERE tic_scr_id = %s AND tic_status = %s ORDER BY tic_row, tic_seat"
        results = self.db.execute_safe(query, (screening_id, status))
        
        return [Ticket(**row) for row in results]

    def get_by_seat(self, screening_id: str, row: str, seat: int) -> Optional[Ticket]:
        """Obtener ticket por asiento específico"""
        query = "SELECT * FROM tb_ticket WHERE tic_scr_id = %s AND tic_row = %s AND tic_seat = %s"
        result = self.db.execute_safe(query, (screening_id, row, seat))
        
        if result:
            return Ticket(**result[0])
        return None

    def get_by_status(self, status: str) -> List[Ticket]:
        """Obtener tickets por estado"""
        query = "SELECT * FROM tb_ticket WHERE tic_status = %s ORDER BY tic_scr_id, tic_row, tic_seat"
        results = self.db.execute_safe(query, (status,))
        
        return [Ticket(**row) for row in results]

    def update(self, ticket_id: str, ticket_data: Dict[str, Any]) -> Optional[Ticket]:
        """Actualizar ticket"""
        # Construir query de actualización dinámicamente
        set_clauses = []
        params = []
        
        for key, value in ticket_data.items():
            if value is not None:
                set_clauses.append(f"{key} = %s")
                params.append(value)
        
        if not set_clauses:
            return self.get_by_id(ticket_id)
        
        # Agregar timestamp de actualización
        set_clauses.append("tic_updated = CURRENT_TIMESTAMP")
        params.append(ticket_id)
        
        query = f"UPDATE tb_ticket SET {', '.join(set_clauses)} WHERE tic_id = %s"
        
        success = self.db.execute_safe(query, tuple(params))
        
        if success:
            return self.get_by_id(ticket_id)
        return None

    def delete(self, ticket_id: str) -> bool:
        """Eliminar ticket"""
        query = "DELETE FROM tb_ticket WHERE tic_id = %s"
        return self.db.execute_safe(query, (ticket_id,)) is not None

    def update_status(self, ticket_id: str, status: str) -> bool:
        """Actualizar estado del ticket"""
        query = "UPDATE tb_ticket SET tic_status = %s, tic_updated = CURRENT_TIMESTAMP WHERE tic_id = %s"
        return self.db.execute_safe(query, (status, ticket_id)) is not None

    def reserve_ticket(self, ticket_id: str) -> bool:
        """Reservar ticket"""
        return self.update_status(ticket_id, 'reserved')

    def sell_ticket(self, ticket_id: str) -> bool:
        """Vender ticket"""
        return self.update_status(ticket_id, 'sold')

    def release_ticket(self, ticket_id: str) -> bool:
        """Liberar ticket (volver a disponible)"""
        return self.update_status(ticket_id, 'available')
