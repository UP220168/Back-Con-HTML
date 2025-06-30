from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TicketStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"

class Ticket(BaseModel):
    tic_id: str
    tic_row: str = Field(..., description="Fila del asiento (A, B, C, etc.)")
    tic_seat: int = Field(..., gt=0, description="Número del asiento")
    tic_scr_id: str = Field(..., description="ID de la proyección")
    tic_status: TicketStatus = Field(default=TicketStatus.AVAILABLE)
    tic_created: Optional[datetime] = None
    tic_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    tic_row: str = Field(..., description="Fila del asiento (A, B, C, etc.)")
    tic_seat: int = Field(..., gt=0, description="Número del asiento")
    tic_scr_id: str = Field(..., description="ID de la proyección")
    tic_status: Optional[TicketStatus] = TicketStatus.AVAILABLE

class TicketUpdate(BaseModel):
    tic_row: Optional[str] = None
    tic_seat: Optional[int] = Field(None, gt=0)
    tic_scr_id: Optional[str] = None
    tic_status: Optional[TicketStatus] = None

class TicketResponse(BaseModel):
    tic_id: str
    tic_row: str
    tic_seat: int
    tic_scr_id: str
    tic_status: TicketStatus
    tic_created: Optional[datetime] = None
    tic_updated: Optional[datetime] = None

    @classmethod
    def from_ticket(cls, ticket: Ticket) -> "TicketResponse":
        return cls(**ticket.model_dump())
