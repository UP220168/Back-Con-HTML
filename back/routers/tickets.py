from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models.ticket import Ticket, TicketCreate, TicketUpdate
from services.ticket_service import TicketService

router = APIRouter(tags=["tickets"])
ticket_service = TicketService()

@router.post("/", response_model=Ticket)
def create_ticket(ticket: TicketCreate):
    """Create a new ticket"""
    try:
        return ticket_service.create_ticket(ticket)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Ticket])
def get_all_tickets():
    """Get all tickets"""
    try:
        return ticket_service.get_all_tickets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: int):
    """Get a specific ticket by ID"""
    try:
        ticket = ticket_service.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: int, ticket_update: TicketUpdate):
    """Update a ticket"""
    try:
        updated_ticket = ticket_service.update_ticket(ticket_id, ticket_update)
        if not updated_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return updated_ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int):
    """Delete a ticket"""
    try:
        success = ticket_service.delete_ticket(ticket_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return {"message": "Ticket deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/screening/{screening_id}", response_model=List[Ticket])
def get_tickets_by_screening(screening_id: int):
    """Get all tickets for a specific screening"""
    try:
        return ticket_service.get_tickets_by_screening(screening_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=List[Ticket])
def get_tickets_by_user(user_id: int):
    """Get all tickets for a specific user"""
    try:
        return ticket_service.get_tickets_by_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{status}", response_model=List[Ticket])
def get_tickets_by_status(status: str):
    """Get all tickets with a specific status"""
    try:
        return ticket_service.get_tickets_by_status(status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{ticket_id}/status")
def update_ticket_status(ticket_id: int, status: str):
    """Update ticket status"""
    try:
        success = ticket_service.update_ticket_status(ticket_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return {"message": f"Ticket status updated to {status}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{ticket_id}/cancel")
def cancel_ticket(ticket_id: int):
    """Cancel a ticket"""
    try:
        success = ticket_service.cancel_ticket(ticket_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ticket not found or cannot be cancelled")
        return {"message": "Ticket cancelled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
