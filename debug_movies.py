#!/usr/bin/env python3
# Script para debuggear el estado de las películas

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

from db_connection import database

def check_movies():
    """Verificar el estado de las películas en la base de datos"""
    try:
        # Consultar todas las películas
        query = """
        SELECT mov_id, mov_title, mov_status, mov_created
        FROM tb_movie 
        ORDER BY mov_status DESC, mov_created DESC
        """
        
        movies = database.execute_safe(query)
        
        print("🎬 Estado de las películas en la base de datos:")
        print("=" * 60)
        
        if not movies:
            print("❌ No se encontraron películas en la base de datos")
            return
        
        active_count = 0
        inactive_count = 0
        
        for movie in movies:
            status_icon = "✅" if movie['mov_status'] == 'active' else "❌"
            print(f"{status_icon} {movie['mov_title']} - {movie['mov_status']} - {movie['mov_id']}")
            
            if movie['mov_status'] == 'active':
                active_count += 1
            else:
                inactive_count += 1
        
        print("=" * 60)
        print(f"📊 Resumen:")
        print(f"   Total: {len(movies)} películas")
        print(f"   Activas: {active_count}")
        print(f"   Inactivas: {inactive_count}")
        
        # Probar el endpoint directamente
        print("\n🔗 Probando consulta con include_inactive=True:")
        
        query_all = """
        SELECT mov_id, mov_title, mov_status
        FROM tb_movie 
        ORDER BY mov_status DESC, mov_created DESC
        LIMIT 100 OFFSET 0
        """
        
        all_movies = database.execute_safe(query_all)
        print(f"   Consulta ALL devolvió: {len(all_movies)} películas")
        
        for movie in all_movies:
            status_icon = "✅" if movie['mov_status'] == 'active' else "❌"
            print(f"     {status_icon} {movie['mov_title']} - {movie['mov_status']}")
            
    except Exception as e:
        print(f"❌ Error verificando películas: {e}")

if __name__ == "__main__":
    check_movies()
