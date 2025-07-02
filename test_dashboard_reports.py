#!/usr/bin/env python3
"""
Script para probar los nuevos reportes del dashboard
"""

import requests
import json
from datetime import datetime

# Configuración
API_BASE_URL = "http://localhost:5000/api"

def test_endpoint(endpoint_name, url):
    """Probar un endpoint y mostrar los resultados"""
    print(f"\n🔍 Probando: {endpoint_name}")
    print(f"📡 URL: {url}")
    
    try:
        response = requests.get(url, headers={"Accept": "application/json"})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Datos recibidos:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"💥 Excepción: {str(e)}")

def main():
    """Función principal"""
    print("🎬 PROBANDO NUEVOS REPORTES DEL DASHBOARD")
    print("=" * 50)
    
    # Probar todos los endpoints de reportes
    endpoints = [
        ("Total de Ventas", f"{API_BASE_URL}/reports/sales/total"),
        ("Total de Clientes", f"{API_BASE_URL}/reports/customers/total"),
        ("Ventas por Membresía", f"{API_BASE_URL}/reports/sales/membership"),
        ("Boletos por Película", f"{API_BASE_URL}/reports/tickets/by-movie"),
        ("Boletos por Sala", f"{API_BASE_URL}/reports/tickets/by-auditorium"),
        ("Película Más Vendida", f"{API_BASE_URL}/reports/movies/most-sold"),
        ("Película Menos Vendida", f"{API_BASE_URL}/reports/movies/least-sold"),
        ("Dashboard General", f"{API_BASE_URL}/reports/dashboard")
    ]
    
    for name, url in endpoints:
        test_endpoint(name, url)
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas!")
    
    # Resumen
    print("\n📋 RESUMEN DE DATOS DISPONIBLES:")
    try:
        # Boletos por película
        response = requests.get(f"{API_BASE_URL}/reports/tickets/by-movie")
        if response.status_code == 200:
            data = response.json()
            total_movies = len(data.get('movies', []))
            movies_with_sales = len([m for m in data.get('movies', []) if m['total_tickets_sold'] > 0])
            print(f"🎬 Películas: {total_movies} total, {movies_with_sales} con ventas")
        
        # Boletos por sala
        response = requests.get(f"{API_BASE_URL}/reports/tickets/by-auditorium")
        if response.status_code == 200:
            data = response.json()
            total_auditoriums = len(data.get('auditoriums', []))
            auditoriums_with_sales = len([a for a in data.get('auditoriums', []) if a['total_tickets_sold'] > 0])
            print(f"🏛️ Salas: {total_auditoriums} total, {auditoriums_with_sales} con ventas")
        
        # Película más vendida
        response = requests.get(f"{API_BASE_URL}/reports/movies/most-sold")
        if response.status_code == 200:
            data = response.json()
            movie = data.get('movie')
            if movie:
                print(f"🏆 Más vendida: {movie['movie_title']} ({movie['total_tickets_sold']} boletos)")
            else:
                print("🏆 Más vendida: No hay datos")
        
        # Película menos vendida
        response = requests.get(f"{API_BASE_URL}/reports/movies/least-sold")
        if response.status_code == 200:
            data = response.json()
            movie = data.get('movie')
            if movie:
                print(f"📉 Menos vendida: {movie['movie_title']} ({movie['total_tickets_sold']} boletos)")
            else:
                print("📉 Menos vendida: No hay datos")
                
    except Exception as e:
        print(f"❌ Error obteniendo resumen: {str(e)}")

if __name__ == "__main__":
    main()
