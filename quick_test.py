#!/usr/bin/env python3
"""
Verificación rápida del sistema después de las correcciones
"""

import requests

def quick_test():
    print("🔍 Verificación rápida del sistema de funciones...")
    
    # Verificar backend
    try:
        response = requests.get("http://localhost:5000/api/movies/")
        movies = response.json().get("movies", [])
        print(f"✅ API Movies: {len(movies)} películas")
        
        response = requests.get("http://localhost:5000/api/auditoriums/")
        auditoriums = response.json().get("auditoriums", [])
        print(f"✅ API Auditoriums: {len(auditoriums)} salas")
        
        response = requests.get("http://localhost:5000/api/screenings/")
        data = response.json()
        screenings = data.get("screenings", [])
        total = data.get("total", 0)
        print(f"✅ API Screenings: {total} funciones")
        
    except Exception as e:
        print(f"❌ Error de API: {e}")
        return False
    
    # Verificar que el frontend esté corriendo
    try:
        response = requests.get("http://localhost:8080", timeout=2)
        if response.status_code == 200:
            print("✅ Frontend servidor funcionando")
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend no responde: {e}")
        return False
    
    print("\n🎯 Sistema verificado:")
    print(f"   • {len(movies)} películas en la base de datos")
    print(f"   • {len(auditoriums)} auditoriums disponibles")
    print(f"   • {total} funciones programadas")
    print("\n🌐 Todo listo para probar en: http://localhost:8080/#screenings")
    
    return True

if __name__ == "__main__":
    quick_test()
