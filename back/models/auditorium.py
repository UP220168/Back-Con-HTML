from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# Enums para validación
class RowFormat(str, Enum):
    LETTERS = "letters"
    NUMBERS = "numbers"

# Modelo base con campos comunes
class AuditoriumBase(BaseModel):
    aud_name: str = Field(..., min_length=1, max_length=100, description="Nombre del auditorio")
    aud_total_rows: int = Field(..., gt=0, le=50, description="Total de filas")
    aud_seats_per_row: int = Field(..., gt=0, le=50, description="Asientos por fila")
    aud_row_format: RowFormat = Field(default=RowFormat.LETTERS, description="Formato de numeración de filas")

# Para crear auditorios (POST)
class AuditoriumCreate(AuditoriumBase):
    pass

# Para actualizar auditorios (PUT/PATCH)
class AuditoriumUpdate(BaseModel):
    aud_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del auditorio")
    aud_total_rows: Optional[int] = Field(None, gt=0, le=50, description="Total de filas")
    aud_seats_per_row: Optional[int] = Field(None, gt=0, le=50, description="Asientos por fila")
    aud_row_format: Optional[RowFormat] = Field(None, description="Formato de numeración de filas")

# Para respuestas completas (GET)
class AuditoriumResponse(AuditoriumBase):
    aud_id: str = Field(..., description="ID único del auditorio")
    aud_created: datetime = Field(..., description="Fecha de creación")
    aud_updated: datetime = Field(..., description="Fecha de última actualización")
    total_capacity: int = Field(..., description="Capacidad total calculada")

    class Config:
        from_attributes = True

# Para listas resumidas
class AuditoriumSummary(BaseModel):
    aud_id: str = Field(..., description="ID único del auditorio")
    aud_name: str = Field(..., description="Nombre del auditorio")
    aud_total_rows: int = Field(..., description="Total de filas")
    aud_seats_per_row: int = Field(..., description="Asientos por fila")
    total_capacity: int = Field(..., description="Capacidad total")

    class Config:
        from_attributes = True
