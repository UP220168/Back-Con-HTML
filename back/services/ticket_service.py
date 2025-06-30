from typing import List, Optional
from models.ticket import Ticket, TicketCreate, TicketUpdate
from repositories.ticket_repository import TicketRepository
from repositories.screening_repository import ScreeningRepository

class TicketService:
    def __init__(self):
        self.ticket_repository = TicketRepository()
        self.screening_repository = ScreeningRepository()
    
    def create_ticket(self, ticket_data: TicketCreate) -> Ticket:
        """Crear un nuevo ticket"""
        # Verificar que la proyección existe
        screening = self.screening_repository.get_by_id(ticket_data.tic_scr_id)
        if not screening:
            raise ValueError("La proyección especificada no existe")
        
        # Verificar que el asiento no esté ocupado
        existing_ticket = self.ticket_repository.get_by_seat(
            ticket_data.tic_scr_id, 
            ticket_data.tic_row, 
            ticket_data.tic_seat
        )
        if existing_ticket:
            raise ValueError("El asiento ya está ocupado")
        
        # Crear el ticket
        ticket_dict = ticket_data.model_dump()
        return self.ticket_repository.create(ticket_dict)
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Obtener ticket por ID"""
        return self.ticket_repository.get_by_id(ticket_id)
    
    def get_all_tickets(self) -> List[Ticket]:
        """Obtener todos los tickets"""
        return self.ticket_repository.get_all()
    
    def get_tickets_by_screening(self, screening_id: str) -> List[Ticket]:
        """Obtener tickets por proyección"""
        return self.ticket_repository.get_by_screening(screening_id)
    
    def get_available_tickets(self, screening_id: str) -> List[Ticket]:
        """Obtener tickets disponibles para una proyección"""
        return self.ticket_repository.get_by_screening_and_status(screening_id, 'available')
    
    def get_reserved_tickets(self, screening_id: str) -> List[Ticket]:
        """Obtener tickets reservados para una proyección"""
        return self.ticket_repository.get_by_screening_and_status(screening_id, 'reserved')
    
    def get_sold_tickets(self, screening_id: str) -> List[Ticket]:
        """Obtener tickets vendidos para una proyección"""
        return self.ticket_repository.get_by_screening_and_status(screening_id, 'sold')
    
    def get_tickets_by_status(self, status: str) -> List[Ticket]:
        """Obtener tickets por estado"""
        return self.ticket_repository.get_by_status(status)
    
    def update_ticket(self, ticket_id: str, ticket_data: TicketUpdate) -> Optional[Ticket]:
        """Actualizar ticket"""
        # Verificar que el ticket existe
        existing_ticket = self.ticket_repository.get_by_id(ticket_id)
        if not existing_ticket:
            return None
        
        # Validar referencias si se están actualizando
        ticket_dict = ticket_data.model_dump(exclude_unset=True)
        
        if 'tic_scr_id' in ticket_dict:
            screening = self.screening_repository.get_by_id(ticket_dict['tic_scr_id'])
            if not screening:
                raise ValueError("La proyección especificada no existe")
        
        # Si se está cambiando de asiento, verificar disponibilidad
        if ('tic_row' in ticket_dict or 'tic_seat' in ticket_dict):
            new_row = ticket_dict.get('tic_row', existing_ticket.tic_row)
            new_seat = ticket_dict.get('tic_seat', existing_ticket.tic_seat)
            screening_id = ticket_dict.get('tic_scr_id', existing_ticket.tic_scr_id)
            
            # Solo verificar si es un cambio real de asiento
            if (new_row != existing_ticket.tic_row or 
                new_seat != existing_ticket.tic_seat or 
                screening_id != existing_ticket.tic_scr_id):
                
                existing_in_seat = self.ticket_repository.get_by_seat(screening_id, new_row, new_seat)
                if existing_in_seat and existing_in_seat.tic_id != ticket_id:
                    raise ValueError("El asiento ya está ocupado")
        
        return self.ticket_repository.update(ticket_id, ticket_dict)
    
    def delete_ticket(self, ticket_id: str) -> bool:
        """Eliminar ticket"""
        return self.ticket_repository.delete(ticket_id)
    
    def reserve_ticket(self, ticket_id: str) -> bool:
        """Reservar ticket"""
        # Verificar que el ticket existe y está disponible
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("El ticket no existe")
        
        if ticket.tic_status != 'available':
            raise ValueError("El ticket no está disponible para reserva")
        
        return self.ticket_repository.reserve_ticket(ticket_id)
    
    def sell_ticket(self, ticket_id: str) -> bool:
        """Vender ticket"""
        # Verificar que el ticket existe y está disponible o reservado
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("El ticket no existe")
        
        if ticket.tic_status not in ['available', 'reserved']:
            raise ValueError("El ticket no está disponible para venta")
        
        return self.ticket_repository.sell_ticket(ticket_id)
    
    def release_ticket(self, ticket_id: str) -> bool:
        """Liberar ticket (volver a disponible)"""
        # Verificar que el ticket existe
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("El ticket no existe")
        
        return self.ticket_repository.release_ticket(ticket_id)
    
    def get_seating_map(self, screening_id: str) -> dict:
        """Obtener mapa de asientos para una proyección"""
        tickets = self.get_tickets_by_screening(screening_id)
        
        seating_map = {}
        for ticket in tickets:
            if ticket.tic_row not in seating_map:
                seating_map[ticket.tic_row] = {}
            seating_map[ticket.tic_row][ticket.tic_seat] = {
                'ticket_id': ticket.tic_id,
                'status': ticket.tic_status
            }
        
        return seating_map
