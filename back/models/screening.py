from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from enum import Enum

class ScreeningStatus(str, Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    FINISHED = "finished"
    CANCELLED = "cancelled"

class Screening(BaseModel):
    scr_id: str
    scr_mov_id: str = Field(..., description="ID de la película")
    scr_aud_id: str = Field(..., description="ID del auditorio")
    scr_date: date = Field(..., description="Fecha de la proyección")
    scr_time: time = Field(..., description="Hora de la proyección")
    scr_price: float = Field(..., gt=0, description="Precio del boleto")
    scr_available_seats: int = Field(default=0, description="Asientos disponibles")
    scr_status: ScreeningStatus = Field(default=ScreeningStatus.SCHEDULED)
    scr_created: Optional[datetime] = None
    scr_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

class ScreeningCreate(BaseModel):
    scr_mov_id: str = Field(..., description="ID de la película")
    scr_aud_id: str = Field(..., description="ID del auditorio")
    scr_date: date = Field(..., description="Fecha de la proyección")
    scr_time: time = Field(..., description="Hora de la proyección")
    scr_price: float = Field(..., gt=0, description="Precio del boleto")
    scr_status: Optional[ScreeningStatus] = ScreeningStatus.SCHEDULED

class ScreeningUpdate(BaseModel):
    scr_mov_id: Optional[str] = None
    scr_aud_id: Optional[str] = None
    scr_date: Optional[date] = None
    scr_time: Optional[time] = None
    scr_price: Optional[float] = Field(None, gt=0)
    scr_available_seats: Optional[int] = None
    scr_status: Optional[ScreeningStatus] = None

class ScreeningResponse(BaseModel):
    scr_id: str
    scr_mov_id: str
    scr_aud_id: str
    scr_date: date
    scr_time: time
    scr_price: float
    scr_available_seats: int
    scr_status: ScreeningStatus
    scr_created: Optional[datetime] = None
    scr_updated: Optional[datetime] = None

    @classmethod
    def from_screening(cls, screening: Screening) -> "ScreeningResponse":
        return cls(**screening.model_dump())

class ScreeningSummary(BaseModel):
    scr_id: str
    scr_mov_id: str
    scr_aud_id: str
    scr_date: date
    scr_time: time
    scr_price: float
    scr_available_seats: int
    scr_status: ScreeningStatus

    class Config:
        from_attributes = True
