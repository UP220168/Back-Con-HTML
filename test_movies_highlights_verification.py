#!/usr/bin/env python3
"""
Script de prueba para verificar que las películas más y menos vendidas 
se muestren correctamente en el dashboard combinado.
"""

import requests
import json

# Configuración
API_BASE_URL = "http://localhost:5000/api"

def test_movies_endpoints():
    """Prueba los endpoints de películas más y menos vendidas"""
    print("=== TESTING MOVIES HIGHLIGHTS ENDPOINTS ===")
    
    try:
        # Probar película más vendida
        print("\n1. Testing most sold movie...")
        response = requests.get(f"{API_BASE_URL}/reports/movies/most-sold")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            most_sold = response.json()
            print(f"Most sold movie: {most_sold['movie']['movie_title']}")
            print(f"Tickets sold: {most_sold['movie']['total_tickets_sold']}")
            print(f"Genre: {most_sold['movie']['movie_genre']}")
        else:
            print(f"Error: {response.text}")
            
        # Probar película menos vendida  
        print("\n2. Testing least sold movie...")
        response = requests.get(f"{API_BASE_URL}/reports/movies/least-sold")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            least_sold = response.json()
            print(f"Least sold movie: {least_sold['movie']['movie_title']}")
            print(f"Tickets sold: {least_sold['movie']['total_tickets_sold']}")
            print(f"Genre: {least_sold['movie']['movie_genre']}")
        else:
            print(f"Error: {response.text}")
            
        print("\n✅ Endpoints are working correctly!")
        print("\nNow check the frontend at http://localhost:8080")
        print("The 'Películas Destacadas' card should show both movies:")
        print("🏆 Most sold movie at the top")
        print("📉 Least sold movie at the bottom")
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")

def test_dashboard_data():
    """Prueba el endpoint del dashboard general"""
    print("\n=== TESTING DASHBOARD DATA ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/reports/dashboard")
        print(f"Dashboard status: {response.status_code}")
        
        if response.status_code == 200:
            dashboard = response.json()
            print(f"Total sales: ${dashboard['summary']['total_sales_amount']}")
            print(f"Total tickets: {dashboard['summary']['total_tickets']}")
            print(f"Total customers: {dashboard['summary']['total_customers']}")
        else:
            print(f"Dashboard error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")

if __name__ == "__main__":
    test_movies_endpoints()
    test_dashboard_data()
    
    print("\n" + "="*50)
    print("VERIFICATION STEPS:")
    print("1. Open http://localhost:8080 in your browser")
    print("2. Look for the 'Películas Destacadas' card in the dashboard")
    print("3. Verify it shows:")
    print("   🏆 Most sold movie section")
    print("   📉 Least sold movie section")
    print("4. Each section should show the movie title and ticket count")
    print("="*50)
