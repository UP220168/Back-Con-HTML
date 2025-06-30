from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, date
from models.screening import Screening, ScreeningCreate, ScreeningUpdate
from services.screening_service import ScreeningService

router = APIRouter(tags=["screenings"])
screening_service = ScreeningService()

@router.post("/", response_model=Screening)
def create_screening(screening: ScreeningCreate):
    """Create a new screening"""
    try:
        return screening_service.create_screening(screening)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Screening])
def get_all_screenings():
    """Get all screenings"""
    try:
        return screening_service.get_all_screenings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{screening_id}", response_model=Screening)
def get_screening(screening_id: int):
    """Get a specific screening by ID"""
    try:
        screening = screening_service.get_screening_by_id(screening_id)
        if not screening:
            raise HTTPException(status_code=404, detail="Screening not found")
        return screening
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{screening_id}", response_model=Screening)
def update_screening(screening_id: int, screening_update: ScreeningUpdate):
    """Update a screening"""
    try:
        updated_screening = screening_service.update_screening(screening_id, screening_update)
        if not updated_screening:
            raise HTTPException(status_code=404, detail="Screening not found")
        return updated_screening
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{screening_id}")
def delete_screening(screening_id: int):
    """Delete a screening"""
    try:
        success = screening_service.delete_screening(screening_id)
        if not success:
            raise HTTPException(status_code=404, detail="Screening not found")
        return {"message": "Screening deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/movie/{movie_id}", response_model=List[Screening])
def get_screenings_by_movie(movie_id: int):
    """Get all screenings for a specific movie"""
    try:
        return screening_service.get_screenings_by_movie(movie_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auditorium/{auditorium_id}", response_model=List[Screening])
def get_screenings_by_auditorium(auditorium_id: int):
    """Get all screenings for a specific auditorium"""
    try:
        return screening_service.get_screenings_by_auditorium(auditorium_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/date/{screening_date}", response_model=List[Screening])
def get_screenings_by_date(screening_date: date):
    """Get all screenings for a specific date"""
    try:
        return screening_service.get_screenings_by_date(screening_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available/{screening_id}")
def get_available_seats(screening_id: int):
    """Get available seats for a screening"""
    try:
        available_seats = screening_service.get_available_seats(screening_id)
        return {"screening_id": screening_id, "available_seats": available_seats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
