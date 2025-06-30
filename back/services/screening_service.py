from typing import List, Optional
from models.screening import Screening, ScreeningCreate, ScreeningUpdate
from repositories.screening_repository import ScreeningRepository
from repositories.movie_repository import MovieRepository
from repositories.auditorium_repository import AuditoriumRepository
from datetime import date, time, datetime, timedelta

class ScreeningService:
    def __init__(self):
        self.screening_repository = ScreeningRepository()
        self.movie_repository = MovieRepository()
        self.auditorium_repository = AuditoriumRepository()
    
    def create_screening(self, screening_data: ScreeningCreate) -> Screening:
        """Crear una nueva proyección"""
        # Verificar que la película existe
        movie = self.movie_repository.get_by_id(screening_data.scr_mov_id)
        if not movie:
            raise ValueError("La película especificada no existe")
        
        # Verificar que el auditorio existe
        auditorium = self.auditorium_repository.get_by_id(screening_data.scr_aud_id)
        if not auditorium:
            raise ValueError("El auditorio especificado no existe")
        
        # Verificar que no hay conflictos de horario
        existing_screenings = self.screening_repository.get_by_auditorium(screening_data.scr_aud_id)
        for existing in existing_screenings:
            if (existing.scr_date == screening_data.scr_date and 
                existing.scr_status in ['scheduled', 'ongoing']):
                # Verificar solapamiento de horarios (asumiendo 2 horas por película)
                existing_start = datetime.combine(existing.scr_date, existing.scr_time)
                existing_end = existing_start + timedelta(hours=2)
                new_start = datetime.combine(screening_data.scr_date, screening_data.scr_time)
                new_end = new_start + timedelta(hours=2)
                
                if (new_start < existing_end and new_end > existing_start):
                    raise ValueError("Ya existe una proyección en ese horario en el auditorio")
        
        # Crear la proyección
        screening_dict = screening_data.model_dump()
        return self.screening_repository.create(screening_dict)
    
    def get_screening(self, screening_id: str) -> Optional[Screening]:
        """Obtener proyección por ID"""
        return self.screening_repository.get_by_id(screening_id)
    
    def get_all_screenings(self) -> List[Screening]:
        """Obtener todas las proyecciones"""
        return self.screening_repository.get_all()
    
    def get_screenings_by_movie(self, movie_id: str) -> List[Screening]:
        """Obtener proyecciones por película"""
        return self.screening_repository.get_by_movie(movie_id)
    
    def get_screenings_by_auditorium(self, auditorium_id: str) -> List[Screening]:
        """Obtener proyecciones por auditorio"""
        return self.screening_repository.get_by_auditorium(auditorium_id)
    
    def get_screenings_by_date(self, date: str) -> List[Screening]:
        """Obtener proyecciones por fecha"""
        return self.screening_repository.get_by_date(date)
    
    def get_screenings_by_status(self, status: str) -> List[Screening]:
        """Obtener proyecciones por estado"""
        return self.screening_repository.get_by_status(status)
    
    def update_screening(self, screening_id: str, screening_data: ScreeningUpdate) -> Optional[Screening]:
        """Actualizar proyección"""
        # Verificar que la proyección existe
        existing_screening = self.screening_repository.get_by_id(screening_id)
        if not existing_screening:
            return None
        
        # Validar referencias si se están actualizando
        screening_dict = screening_data.model_dump(exclude_unset=True)
        
        if 'scr_mov_id' in screening_dict:
            movie = self.movie_repository.get_by_id(screening_dict['scr_mov_id'])
            if not movie:
                raise ValueError("La película especificada no existe")
        
        if 'scr_aud_id' in screening_dict:
            auditorium = self.auditorium_repository.get_by_id(screening_dict['scr_aud_id'])
            if not auditorium:
                raise ValueError("El auditorio especificado no existe")
        
        return self.screening_repository.update(screening_id, screening_dict)
    
    def delete_screening(self, screening_id: str) -> bool:
        """Eliminar proyección"""
        return self.screening_repository.delete(screening_id)
    
    def update_available_seats(self, screening_id: str, seats: int) -> bool:
        """Actualizar asientos disponibles"""
        return self.screening_repository.update_available_seats(screening_id, seats)
    
    def get_upcoming_screenings(self, days: int = 7) -> List[Screening]:
        """Obtener proyecciones próximas"""
        screenings = self.screening_repository.get_all()
        current_date = date.today()
        end_date = current_date + timedelta(days=days)
        
        upcoming = []
        for screening in screenings:
            if (current_date <= screening.scr_date <= end_date and 
                screening.scr_status in ['scheduled', 'ongoing']):
                upcoming.append(screening)
        
        return upcoming
