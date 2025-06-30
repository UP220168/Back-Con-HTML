#!/usr/bin/env python3
"""
Script de validación automatizada para endpoints de reportes
Sistema de Gestión de Cine - FastAPI Backend
"""

import requests
import json
from datetime import datetime, date
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:5000/api/reports"
ENDPOINTS = {
    "a_total_sales": "/sales/total",
    "b_customers_total": "/customers/total", 
    "c_d_sales_membership": "/sales/membership",
    "e_tickets_by_movie": "/tickets/by-movie",
    "f_tickets_by_auditorium": "/tickets/by-auditorium",
    "g_most_sold_movie": "/movies/most-sold",
    "h_least_sold_movie": "/movies/least-sold",
    "dashboard": "/dashboard"
}

def test_endpoint(endpoint_name: str, url: str) -> Dict[str, Any]:
    """Prueba un endpoint específico y retorna el resultado."""
    full_url = BASE_URL + url
    
    try:
        print(f"\n🔍 Probando {endpoint_name}: {url}")
        response = requests.get(full_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {endpoint_name}: OK")
            return {
                "status": "success",
                "endpoint": endpoint_name,
                "url": url,
                "data": data,
                "response_time": response.elapsed.total_seconds()
            }
        else:
            print(f"❌ {endpoint_name}: Error {response.status_code}")
            return {
                "status": "error",
                "endpoint": endpoint_name,
                "url": url,
                "error": f"HTTP {response.status_code}: {response.text}",
                "response_time": response.elapsed.total_seconds()
            }
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint_name}: Excepción - {str(e)}")
        return {
            "status": "exception",
            "endpoint": endpoint_name,
            "url": url,
            "error": str(e),
            "response_time": None
        }

def format_results(results: Dict[str, Any]) -> None:
    """Formatea y muestra los resultados de manera legible."""
    
    print("\n" + "="*80)
    print("📊 RESUMEN DE RESULTADOS DE ENDPOINTS DE REPORTES")
    print("="*80)
    
    successful = 0
    failed = 0
    
    for endpoint_name, result in results.items():
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"\n{status_icon} {endpoint_name.upper().replace('_', ' ')}")
        print(f"   URL: {result['url']}")
        
        if result["status"] == "success":
            successful += 1
            data = result["data"]
            response_time = result["response_time"]
            print(f"   Tiempo de respuesta: {response_time:.3f}s")
            
            # Mostrar datos relevantes según el endpoint
            if "total_sales" in endpoint_name:
                if "total_sales_count" in data:
                    print(f"   Total ventas: {data['total_sales_count']}")
                    print(f"   Monto total: ${data['total_sales_amount']}")
                    
            elif "customers" in endpoint_name:
                if "total_customers_served" in data:
                    print(f"   Clientes atendidos: {data['total_customers_served']}")
                    
            elif "membership" in endpoint_name:
                if "with_membership" in data and "without_membership" in data:
                    with_mem = data["with_membership"]
                    without_mem = data["without_membership"]
                    print(f"   Con membresía: {with_mem['total_sales']} ventas (${with_mem['total_amount']})")
                    print(f"   Sin membresía: {without_mem['total_sales']} ventas (${without_mem['total_amount']})")
                    
            elif "movie" in endpoint_name and "by" not in endpoint_name:
                if "movie" in data and data["movie"]:
                    movie = data["movie"]
                    print(f"   Película: {movie.get('movie_title', 'N/A')}")
                    print(f"   Boletos vendidos: {movie.get('total_tickets_sold', 0)}")
                    print(f"   Ingresos: ${movie.get('total_revenue', 0)}")
                elif "message" in data:
                    print(f"   Mensaje: {data['message']}")
                    
            elif "by_movie" in endpoint_name:
                if "movies" in data:
                    print(f"   Total películas: {len(data['movies'])}")
                    
            elif "by_auditorium" in endpoint_name:
                if "auditoriums" in data:
                    print(f"   Total salas: {len(data['auditoriums'])}")
                    
            elif "dashboard" in endpoint_name:
                if "summary" in data:
                    summary = data["summary"]
                    print(f"   Ventas: {summary.get('total_sales_count', 0)}")
                    print(f"   Ingresos: ${summary.get('total_sales_amount', 0)}")
                    print(f"   Clientes: {summary.get('total_customers', 0)}")
                    print(f"   Boletos: {summary.get('total_tickets', 0)}")
        else:
            failed += 1
            print(f"   Error: {result['error']}")
            if result["response_time"]:
                print(f"   Tiempo de respuesta: {result['response_time']:.3f}s")
    
    print("\n" + "="*80)
    print(f"📈 ESTADÍSTICAS FINALES")
    print("="*80)
    print(f"✅ Exitosos: {successful}/{len(results)}")
    print(f"❌ Fallidos: {failed}/{len(results)}")
    
    if successful == len(results):
        print(f"\n🎉 ¡TODOS LOS ENDPOINTS FUNCIONAN CORRECTAMENTE!")
        print(f"🚀 El sistema está listo para producción.")
    else:
        print(f"\n⚠️  Se encontraron {failed} endpoint(s) con problemas.")
        print(f"🔧 Revisa los errores antes de desplegar a producción.")

def main():
    """Función principal que ejecuta todas las pruebas."""
    print("🚀 INICIANDO VALIDACIÓN DE ENDPOINTS DE REPORTES")
    print("="*80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"📊 Total endpoints a probar: {len(ENDPOINTS)}")
    
    results = {}
    
    # Probar cada endpoint
    for endpoint_name, url in ENDPOINTS.items():
        results[endpoint_name] = test_endpoint(endpoint_name, url)
    
    # Mostrar resultados formateados
    format_results(results)
    
    # Guardar resultados en JSON para análisis posterior
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"reports_validation_{timestamp}.json"
    
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "base_url": BASE_URL,
                "total_endpoints": len(ENDPOINTS),
                "results": results
            }, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados guardados en: {results_file}")
    except Exception as e:
        print(f"\n⚠️  No se pudieron guardar los resultados: {e}")

if __name__ == "__main__":
    main()
