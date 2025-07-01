#!/usr/bin/env python3
"""Script para depurar el endpoint de screenings"""

import asyncio
from repositories.screening_repository import screening_repository
from models.screening import ScreeningSummary
import json
from datetime import datetime, date, time

async def debug_screenings():
    try:
        print("=== DEBUG SCREENINGS ===")
        
        # Obtener datos crudos del repository
        screenings = await screening_repository.get_all(0, 10)
        print(f"Número de proyecciones: {len(screenings)}")
        
        if screenings:
            print("\n=== PRIMERA PROYECCIÓN (datos crudos) ===")
            first_screening = screenings[0]
            print(f"Tipo: {type(first_screening)}")
            
            for key, value in first_screening.items():
                print(f"{key}: {value} (tipo: {type(value)})")
            
            print("\n=== INTENTANDO CREAR ScreeningSummary ===")
            try:
                # Convertir tipos problemáticos usando la misma lógica que el service
                processed_screening = {}
                for key, value in first_screening.items():
                    if key == 'scr_time' and hasattr(value, 'total_seconds'):
                        # Convertir timedelta a time
                        total_seconds = int(value.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        processed_screening[key] = time(hours, minutes, seconds)
                    elif key == 'scr_price' and hasattr(value, '__float__'):
                        # Convertir Decimal a float
                        processed_screening[key] = float(value)
                    else:
                        processed_screening[key] = value
                
                print("\n=== DATOS PROCESADOS ===")
                for key, value in processed_screening.items():
                    print(f"{key}: {value} (tipo: {type(value)})")
                
                summary = ScreeningSummary(**processed_screening)
                print(f"\n✅ ScreeningSummary creado exitosamente: {summary}")
                
            except Exception as e:
                print(f"\n❌ Error creando ScreeningSummary: {str(e)}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error en debug: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_screenings())
