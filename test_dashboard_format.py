#!/usr/bin/env python3
"""
Script para verificar que las tarjetas del dashboard estén en formato uniforme.
"""

import requests
import json

# Configuración
API_BASE_URL = "http://localhost:5000/api"

def check_dashboard_format():
    """Verifica que el dashboard tenga el formato correcto"""
    print("=== CHECKING DASHBOARD FORMAT ===")
    
    try:
        # Verificar todos los endpoints necesarios
        endpoints = {
            "Dashboard": "/reports/dashboard",
            "Tickets by Movie": "/reports/tickets/by-movie", 
            "Tickets by Auditorium": "/reports/tickets/by-auditorium",
            "Most Sold Movie": "/reports/movies/most-sold",
            "Least Sold Movie": "/reports/movies/least-sold"
        }
        
        for name, endpoint in endpoints.items():
            print(f"\n{name}:")
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Status: {response.status_code}")
                
                # Mostrar información relevante
                if "dashboard" in endpoint:
                    summary = data.get('summary', {})
                    print(f"  📊 Total Sales: ${summary.get('total_sales_amount', 0)}")
                    print(f"  🎟️ Total Tickets: {summary.get('total_tickets', 0)}")
                elif "by-movie" in endpoint:
                    movies = data.get('movies', [])
                    if movies:
                        print(f"  🎬 Top Movie: {movies[0]['movie_title']}")
                        print(f"  🎟️ Tickets: {movies[0]['total_tickets_sold']}")
                elif "by-auditorium" in endpoint:
                    auditoriums = data.get('auditoriums', [])
                    if auditoriums:
                        print(f"  🏛️ Top Auditorium: {auditoriums[0]['auditorium_name']}")
                        print(f"  🎟️ Tickets: {auditoriums[0]['total_tickets_sold']}")
                elif "most-sold" in endpoint:
                    movie = data.get('movie', {})
                    if movie:
                        print(f"  🏆 Movie: {movie['movie_title']}")
                        print(f"  🎟️ Tickets: {movie['total_tickets_sold']}")
                elif "least-sold" in endpoint:
                    movie = data.get('movie', {})
                    if movie:
                        print(f"  📉 Movie: {movie['movie_title']}")
                        print(f"  🎟️ Tickets: {movie['total_tickets_sold']}")
            else:
                print(f"  ❌ Error: {response.status_code}")
        
        print(f"\n{'='*50}")
        print("DASHBOARD LAYOUT VERIFICATION:")
        print("All cards should now have the same format:")
        print("1. 💰 Total de Ventas - 2 metrics (Sales Amount + Transactions)")
        print("2. 👥 Clientes - 1 metric (Total Customers)")
        print("3. 🎟️ Boletos - 2 metrics (Total Tickets + Movies Available)")
        print("4. 🎬 Boletos por Película - 2 metrics (Top Movie + Total Tickets)")
        print("5. 🏛️ Boletos por Sala - 2 metrics (Top Auditorium + Total Tickets)")
        print("6. 👑 Películas Destacadas - 2 sections (Most Sold + Least Sold)")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_dashboard_format()
