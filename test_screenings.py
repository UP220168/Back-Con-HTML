#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento de las funciones (screenings)
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración de la API
API_BASE = "http://localhost:5000/api"

def test_api_endpoints():
    """Probar los endpoints básicos de la API"""
    print("🔍 Probando endpoints de la API...")
    
    # Probar películas
    try:
        response = requests.get(f"{API_BASE}/movies/")
        if response.status_code == 200:
            movies = response.json()["movies"]
            print(f"✅ Películas encontradas: {len(movies)}")
            return movies
        else:
            print(f"❌ Error obteniendo películas: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error conectando a la API: {e}")
        return []

def test_auditoriums():
    """Probar el endpoint de auditoriums"""
    try:
        response = requests.get(f"{API_BASE}/auditoriums/")
        if response.status_code == 200:
            auditoriums = response.json()["auditoriums"]
            print(f"✅ Auditoriums encontrados: {len(auditoriums)}")
            return auditoriums
        else:
            print(f"❌ Error obteniendo auditoriums: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error obteniendo auditoriums: {e}")
        return []

def test_screenings():
    """Probar el endpoint de screenings"""
    try:
        response = requests.get(f"{API_BASE}/screenings/")
        if response.status_code == 200:
            data = response.json()
            screenings = data["screenings"]
            print(f"✅ Screenings encontrados: {len(screenings)}")
            return screenings
        else:
            print(f"❌ Error obteniendo screenings: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error obteniendo screenings: {e}")
        return []

def create_test_screening(movie_id, auditorium_id):
    """Crear una función de prueba"""
    # Crear fecha para mañana a las 20:00
    tomorrow = datetime.now() + timedelta(days=1)
    screening_datetime = tomorrow.replace(hour=20, minute=0, second=0, microsecond=0)
    
    screening_data = {
        "scr_mov_id": movie_id,
        "scr_aud_id": auditorium_id,
        "scr_date": screening_datetime.strftime("%Y-%m-%d"),
        "scr_time": screening_datetime.strftime("%H:%M:%S"),
        "scr_price": 120.00
    }
    
    try:
        print(f"📝 Creando función de prueba...")
        print(f"   Película: {movie_id}")
        print(f"   Auditorium: {auditorium_id}")
        print(f"   Fecha/Hora: {screening_datetime}")
        
        response = requests.post(f"{API_BASE}/screenings/", json=screening_data)
        
        if response.status_code == 201:
            screening = response.json()
            print(f"✅ Función creada exitosamente!")
            print(f"   ID: {screening['scr_id']}")
            return screening
        else:
            print(f"❌ Error creando función: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creando función: {e}")
        return None

def main():
    print("🚀 Iniciando pruebas del sistema de gestión de funciones...")
    print("=" * 60)
    
    # Probar endpoints básicos
    movies = test_api_endpoints()
    auditoriums = test_auditoriums()
    screenings = test_screenings()
    
    print("\n" + "=" * 60)
    
    if movies and auditoriums:
        print(f"🎬 Películas disponibles:")
        for movie in movies:
            print(f"   - {movie['mov_title']} (ID: {movie['mov_id'][:8]}...)")
            
        print(f"\n🏛️ Auditoriums disponibles:")
        for aud in auditoriums:
            print(f"   - {aud['aud_name']} (ID: {aud['aud_id'][:8]}...)")
        
        # Crear una función de prueba
        print(f"\n🎯 Creando función de prueba...")
        test_screening = create_test_screening(movies[0]['mov_id'], auditoriums[0]['aud_id'])
        
        if test_screening:
            print(f"\n🔍 Verificando función creada...")
            updated_screenings = test_screenings()
            
            if len(updated_screenings) > len(screenings):
                print(f"✅ ¡Función creada y verificada exitosamente!")
            else:
                print(f"⚠️ La función se creó pero no aparece en la lista")
        
    else:
        print("❌ No se pudieron obtener los datos necesarios para las pruebas")
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas")
    print("\n💡 Ahora puedes abrir el navegador en http://localhost:8080")
    print("   y navegar al módulo de 'Funciones' para probar la interfaz completa")

if __name__ == "__main__":
    main()
