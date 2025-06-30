import os
import sys
from pathlib import Path

# Configurar path del proyecto
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Importar conexión a base de datos
from db_connection import database, database_name

# Crear función de inicialización
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Verificar conexión a base de datos
    try:
        print("🔄 Iniciando conexión a base de datos...")
        # Verificar que la base de datos existe
        exist = database.execute_safe("SHOW DATABASES LIKE %s", (database_name,))
        if len(exist) > 0:
            print(f"✅ Base de datos '{database_name}' conectada exitosamente")
        else:
            print(f"❌ Base de datos '{database_name}' no encontrada")
    except Exception as e:
        print(f"❌ Error conectando a base de datos: {e}")
    
    yield
    
    # Shutdown: Cerrar conexiones si es necesario
    print("🔴 Cerrando aplicación...")

# Importar routers
from routers import movies, auditoriums, users, employees, screenings, tickets, sales, reports

# Crear aplicación FastAPI
app = FastAPI(
    title="Cinema Management API",
    description="API para gestión de cine con FastAPI y MySQL",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "file://", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(movies.router, prefix="/api/movies")
app.include_router(auditoriums.router, prefix="/api/auditoriums")
app.include_router(users.router, prefix="/api/users")
app.include_router(employees.router, prefix="/api/employees")
app.include_router(screenings.router, prefix="/api/screenings")
app.include_router(tickets.router, prefix="/api/tickets")
app.include_router(sales.router, prefix="/api/sales")
app.include_router(reports.router, prefix="/api/reports")

# Ruta básica
@app.get("/")
async def read_root():
    return {
        "message": "Cinema Management API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "movies": "/api/movies/",
            "auditoriums": "/api/auditoriums/",
            "users": "/api/users/",
            "employees": "/api/employees/",
            "screenings": "/api/screenings/",
            "tickets": "/api/tickets/",
            "sales": "/api/sales/",
            "reports": "/api/reports/",
            "health": "/health"
        }
    }

# Health check con conexión a DB
@app.get("/health")
async def health_check():
    try:
        # Probar conexión a la base de datos
        result = database.execute_safe("SELECT 1 as test")
        db_status = "connected" if result else "disconnected"
        
        return {
            "status": "healthy",
            "message": "API funcionando correctamente",
            "database": db_status,
            "database_name": database_name
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": "Error en la conexión",
            "error": str(e),
            "database": "error"
        }

# Endpoint para probar la base de datos
@app.get("/api/test/db")
async def test_database():
    """Probar conexión y consultas a la base de datos"""
    try:
        # Probar consulta básica
        result = database.execute_safe("SELECT VERSION() as mysql_version")
        
        # Probar consulta a tablas
        tables = database.execute_safe("SHOW TABLES")
        
        return {
            "status": "success",
            "mysql_version": result[0]["mysql_version"] if result else "unknown",
            "database_name": database_name,
            "tables": [list(table.values())[0] for table in tables] if tables else [],
            "total_tables": len(tables) if tables else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

# Endpoint para probar consulta a películas
@app.get("/api/test/movies")
async def test_movies():
    """Probar consulta a la tabla de películas"""
    try:
        # Verificar si la tabla existe
        table_check = database.execute_safe(
            "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = %s AND table_name = 'tb_movie'",
            (database_name,)
        )
        
        if not table_check or table_check[0]['count'] == 0:
            return {"status": "warning", "message": "Tabla tb_movie no existe"}
        
        # Obtener películas
        movies = database.execute_safe("SELECT * FROM tb_movie LIMIT 5")
        
        return {
            "status": "success",
            "message": "Consulta exitosa",
            "total_movies": len(movies),
            "movies": movies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando películas: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)