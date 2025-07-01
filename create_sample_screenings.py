#!/usr/bin/env python3
"""
Script para crear más funciones de prueba y tener un conjunto de datos completo
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración de la API
API_BASE = "http://localhost:5000/api"

def create_sample_screenings():
    """Crear varias funciones de ejemplo para diferentes días y horarios"""
    
    # Obtener películas y auditoriums
    movies_response = requests.get(f"{API_BASE}/movies/")
    auditoriums_response = requests.get(f"{API_BASE}/auditoriums/")
    
    if movies_response.status_code != 200 or auditoriums_response.status_code != 200:
        print("❌ No se pudieron obtener datos básicos")
        return
    
    movies = movies_response.json()["movies"]
    auditoriums = auditoriums_response.json()["auditoriums"]
    
    print(f"🎬 Películas disponibles: {len(movies)}")
    print(f"🏛️ Auditoriums disponibles: {len(auditoriums)}")
    
    # Definir horarios comunes para las funciones
    horarios = ["14:00", "17:30", "20:00", "22:30"]
    
    # Crear funciones para los próximos 3 días
    funciones_creadas = 0
    
    for day_offset in range(3):  # Hoy, mañana y pasado mañana
        fecha = datetime.now() + timedelta(days=day_offset)
        fecha_str = fecha.strftime("%Y-%m-%d")
        
        print(f"\n📅 Creando funciones para {fecha_str}...")
        
        for i, auditorium in enumerate(auditoriums):
            # Rotar películas entre auditoriums
            movie = movies[i % len(movies)]
            
            # Crear 2-3 funciones por auditorium por día
            for j in range(min(3, len(horarios))):
                horario = horarios[j]
                
                screening_data = {
                    "scr_mov_id": movie["mov_id"],
                    "scr_aud_id": auditorium["aud_id"],
                    "scr_date": fecha_str,
                    "scr_time": f"{horario}:00",
                    "scr_price": round(100 + (j * 20) + (i * 10), 2)  # Precios variables
                }
                
                try:
                    response = requests.post(f"{API_BASE}/screenings/", json=screening_data)
                    
                    if response.status_code == 201:
                        funciones_creadas += 1
                        print(f"   ✅ {auditorium['aud_name']} - {movie['mov_title']} a las {horario}")
                    else:
                        print(f"   ❌ Error: {auditorium['aud_name']} - {horario} ({response.status_code})")
                        if response.status_code == 400:
                            # Probablemente conflicto de horario, continuar
                            pass
                
                except Exception as e:
                    print(f"   ❌ Error creando función: {e}")
    
    print(f"\n🎯 Total de funciones creadas: {funciones_creadas}")
    
    # Verificar el resultado final
    screenings_response = requests.get(f"{API_BASE}/screenings/")
    if screenings_response.status_code == 200:
        data = screenings_response.json()
        total_screenings = data["total"]
        print(f"📊 Total de funciones en el sistema: {total_screenings}")
    
    return funciones_creadas

def main():
    print("🎭 Creando funciones de ejemplo para el sistema...")
    print("=" * 60)
    
    funciones_creadas = create_sample_screenings()
    
    print("\n" + "=" * 60)
    print("🏁 Proceso completado")
    
    if funciones_creadas > 0:
        print(f"✅ Se crearon {funciones_creadas} funciones exitosamente")
        print("\n💡 Ahora puedes:")
        print("   1. Abrir http://localhost:8080 en tu navegador")
        print("   2. Navegar al módulo de 'Funciones'")
        print("   3. Ver las funciones creadas y probar las funcionalidades")
        print("   4. Agregar, editar o eliminar funciones")
    else:
        print("⚠️ No se crearon funciones nuevas")

if __name__ == "__main__":
    main()
