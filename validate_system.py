#!/usr/bin/env python3
"""
Validación final del sistema de gestión de funciones
"""

import requests
import json

API_BASE = "http://localhost:5000/api"

def validate_system():
    print("🔍 Validando el sistema completo de gestión de funciones...")
    print("=" * 60)
    
    # 1. Verificar películas
    try:
        response = requests.get(f"{API_BASE}/movies/")
        movies_data = response.json()
        movies = movies_data.get("movies", [])
        print(f"✅ Películas: {len(movies)} encontradas")
        for movie in movies[:3]:
            print(f"   - {movie['mov_title']} ({movie['mov_duration']} min)")
    except Exception as e:
        print(f"❌ Error con películas: {e}")
        return False
    
    # 2. Verificar auditoriums
    try:
        response = requests.get(f"{API_BASE}/auditoriums/")
        auditoriums_data = response.json()
        auditoriums = auditoriums_data.get("auditoriums", [])
        print(f"✅ Auditoriums: {len(auditoriums)} encontrados")
        for aud in auditoriums[:3]:
            print(f"   - {aud['aud_name']} ({aud['total_capacity']} asientos)")
    except Exception as e:
        print(f"❌ Error con auditoriums: {e}")
        return False
    
    # 3. Verificar funciones
    try:
        response = requests.get(f"{API_BASE}/screenings/")
        screenings_data = response.json()
        screenings = screenings_data.get("screenings", [])
        total = screenings_data.get("total", 0)
        print(f"✅ Funciones: {total} encontradas")
        
        if len(screenings) > 0:
            print("   Ejemplos de funciones:")
            for screening in screenings[:3]:
                movie = next((m for m in movies if m['mov_id'] == screening['scr_mov_id']), None)
                aud = next((a for a in auditoriums if a['aud_id'] == screening['scr_aud_id']), None)
                
                movie_title = movie['mov_title'] if movie else 'Película no encontrada'
                aud_name = aud['aud_name'] if aud else 'Sala no encontrada'
                
                print(f"   - {movie_title} en {aud_name}")
                print(f"     {screening['scr_date']} a las {screening['scr_time']} - ${screening['scr_price']}")
        else:
            print("   No hay funciones programadas")
            
    except Exception as e:
        print(f"❌ Error con funciones: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 Validación del sistema completada exitosamente")
    print("\n📋 Resumen del sistema:")
    print(f"   • {len(movies)} películas disponibles")
    print(f"   • {len(auditoriums)} salas operativas")
    print(f"   • {total} funciones programadas")
    
    print("\n🌐 Frontend disponible en: http://localhost:8080")
    print("   📝 Para probar el módulo de funciones:")
    print("   1. Abre el navegador en http://localhost:8080")
    print("   2. Navega a 'Funciones' en el menú lateral")
    print("   3. Verifica que se muestren las funciones")
    print("   4. Prueba agregar, editar y eliminar funciones")
    
    print(f"\n🔧 API Backend disponible en: http://localhost:5000")
    print("   📖 Documentación: http://localhost:5000/docs")
    
    return True

if __name__ == "__main__":
    validate_system()
