from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# Enums para validación
class MovieClassification(str, Enum):
    G = "G"
    PG = "PG"
    PG_13 = "PG-13"
    R = "R"
    NC_17 = "NC-17"

class MovieStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# Modelo base con campos comunes
class MovieBase(BaseModel):
    mov_title: str = Field(..., min_length=1, max_length=255, description="Título de la película")
    mov_classification: MovieClassification = Field(..., description="Clasificación de edad")
    mov_duration: int = Field(..., gt=0, le=600, description="Duración en minutos")
    mov_description: Optional[str] = Field(None, max_length=1000, description="Descripción")
    mov_genre: Optional[str] = Field(None, max_length=100, description="Género")

# Para crear películas (POST)
class MovieCreate(MovieBase):
    mov_status: Optional[MovieStatus] = MovieStatus.ACTIVE

# Para actualizar películas (PUT/PATCH)
class MovieUpdate(BaseModel):
    mov_title: Optional[str] = Field(None, min_length=1, max_length=255)
    mov_classification: Optional[MovieClassification] = None
    mov_duration: Optional[int] = Field(None, gt=0, le=600)
    mov_description: Optional[str] = Field(None, max_length=1000)
    mov_genre: Optional[str] = Field(None, max_length=100)
    mov_status: Optional[MovieStatus] = None

# Para respuestas de la API (GET)
class MovieResponse(MovieBase):
    mov_id: str
    mov_status: MovieStatus = MovieStatus.ACTIVE
    mov_created: datetime
    mov_updated: datetime

    class Config:
        from_attributes = True

# Modelo principal (alias de MovieResponse)
class Movie(MovieResponse):
    class Config:
        from_attributes = True

# Modelo simple para listas
class MovieSummary(BaseModel):
    mov_id: str
    mov_title: str
    mov_duration: int
    mov_classification: MovieClassification
    mov_genre: Optional[str] = None
    mov_status: MovieStatus