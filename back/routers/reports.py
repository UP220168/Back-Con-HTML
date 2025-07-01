from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from db_connection import database

router = APIRouter(tags=["reports"])

@router.get("/sales/total")
async def get_total_sales(
    start_date: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)")
):
    """
    a) El total de las ventas realizadas
    """
    try:
        # Query base
        query = """
        SELECT 
            COUNT(*) as total_sales,
            COALESCE(SUM(sal_total_amount), 0) as total_amount
        FROM tb_sale s
        WHERE s.sal_status = 'completed'
        """
        
        params = []
        
        # Agregar filtros de fecha si se proporcionan
        if start_date:
            query += " AND DATE(s.sal_created) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(s.sal_created) <= %s"
            params.append(end_date)
        
        result = database.execute_safe(query, tuple(params) if params else None)
        
        if result:
            return {
                "total_sales_count": result[0]["total_sales"],
                "total_sales_amount": float(result[0]["total_amount"]),
                "start_date": start_date,
                "end_date": end_date
            }
        
        return {
            "total_sales_count": 0,
            "total_sales_amount": 0.0,
            "start_date": start_date,
            "end_date": end_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener total de ventas: {str(e)}")

@router.get("/customers/total")
async def get_total_customers_served(
    start_date: Optional[date] = Query(None, description="Fecha de inicio"),
    end_date: Optional[date] = Query(None, description="Fecha de fin")
):
    """
    b) El número de clientes atendidos
    """
    try:
        query = """
        SELECT COUNT(DISTINCT s.sal_usr_id) as total_customers
        FROM tb_sale s
        WHERE s.sal_status = 'completed'
        AND s.sal_usr_id IS NOT NULL
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(s.sal_created) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(s.sal_created) <= %s"
            params.append(end_date)
        
        result = database.execute_safe(query, tuple(params) if params else None)
        
        return {
            "total_customers_served": result[0]["total_customers"] if result else 0,
            "start_date": start_date,
            "end_date": end_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener clientes atendidos: {str(e)}")

@router.get("/sales/membership")
async def get_sales_by_membership(
    start_date: Optional[date] = Query(None, description="Fecha de inicio"),
    end_date: Optional[date] = Query(None, description="Fecha de fin")
):
    """
    c) Total de ventas a clientes con membresía
    d) Total de ventas a clientes sin membresía
    Nota: Se simulan membresías basadas en cantidad de compras (>= 3 compras = membresía)
    """
    try:
        query = """
        SELECT 
            CASE 
                WHEN customer_sales.total_purchases >= 3 THEN 'with_membership' 
                ELSE 'without_membership' 
            END as membership_type,
            COUNT(*) as total_sales,
            COALESCE(SUM(s.sal_total_amount), 0) as total_amount
        FROM tb_sale s
        LEFT JOIN (
            SELECT 
                sal_usr_id,
                COUNT(*) as total_purchases
            FROM tb_sale 
            WHERE sal_status = 'completed' AND sal_usr_id IS NOT NULL
            GROUP BY sal_usr_id
        ) customer_sales ON s.sal_usr_id = customer_sales.sal_usr_id
        WHERE s.sal_status = 'completed'
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(s.sal_created) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(s.sal_created) <= %s"
            params.append(end_date)
        
        query += " GROUP BY membership_type"
        
        result = database.execute_safe(query, tuple(params) if params else None)
        
        # Organizar resultados
        with_membership = {"total_sales": 0, "total_amount": 0.0}
        without_membership = {"total_sales": 0, "total_amount": 0.0}
        
        if result:
            for row in result:
                if row["membership_type"] == "with_membership":
                    with_membership = {
                        "total_sales": row["total_sales"],
                        "total_amount": float(row["total_amount"])
                    }
                else:
                    without_membership = {
                        "total_sales": row["total_sales"],
                        "total_amount": float(row["total_amount"])
                    }
        
        return {
            "with_membership": with_membership,
            "without_membership": without_membership,
            "start_date": start_date,
            "end_date": end_date,
            "note": "Membresía simulada: clientes con 3+ compras = membresía"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas por membresía: {str(e)}")

@router.get("/tickets/by-movie")
async def get_tickets_by_movie(
    start_date: Optional[date] = Query(None, description="Fecha de inicio"),
    end_date: Optional[date] = Query(None, description="Fecha de fin")
):
    """
    e) El total de boletos vendidos por película
    """
    try:
        query = """
        SELECT 
            m.mov_id,
            m.mov_title,
            m.mov_genre,
            COUNT(s.sal_tic_id) as total_tickets,
            COALESCE(SUM(s.sal_total_amount), 0) as total_revenue
        FROM tb_movie m
        LEFT JOIN tb_screening sc ON m.mov_id = sc.scr_mov_id
        LEFT JOIN tb_sale s ON sc.scr_id = (
            SELECT t.tic_scr_id 
            FROM tb_ticket t 
            WHERE t.tic_id = s.sal_tic_id
        )
        WHERE (s.sal_status = 'completed' OR s.sal_status IS NULL)
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(s.sal_created) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(s.sal_created) <= %s"
            params.append(end_date)
        
        query += " GROUP BY m.mov_id, m.mov_title, m.mov_genre ORDER BY total_tickets DESC"
        
        result = database.execute_safe(query, tuple(params) if params else None)
        
        movies_data = []
        if result:
            for row in result:
                movies_data.append({
                    "movie_id": row["mov_id"],
                    "movie_title": row["mov_title"],
                    "movie_genre": row["mov_genre"],
                    "total_tickets_sold": row["total_tickets"],
                    "total_revenue": float(row["total_revenue"])
                })
        
        return {
            "movies": movies_data,
            "start_date": start_date,
            "end_date": end_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener boletos por película: {str(e)}")

@router.get("/tickets/by-auditorium")
async def get_tickets_by_auditorium(
    start_date: Optional[date] = Query(None, description="Fecha de inicio"),
    end_date: Optional[date] = Query(None, description="Fecha de fin")
):
    """
    f) El total de boletos vendidos por sala
    """
    try:
        query = """
        SELECT 
            a.aud_id,
            a.aud_name,
            (a.aud_total_rows * a.aud_seats_per_row) as total_capacity,
            COUNT(s.sal_tic_id) as total_tickets,
            COALESCE(SUM(s.sal_total_amount), 0) as total_revenue
        FROM tb_auditorium a
        LEFT JOIN tb_screening sc ON a.aud_id = sc.scr_aud_id
        LEFT JOIN tb_sale s ON sc.scr_id = (
            SELECT t.tic_scr_id 
            FROM tb_ticket t 
            WHERE t.tic_id = s.sal_tic_id
        )
        WHERE (s.sal_status = 'completed' OR s.sal_status IS NULL)
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(s.sal_created) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(s.sal_created) <= %s"
            params.append(end_date)
        
        query += " GROUP BY a.aud_id, a.aud_name, a.aud_total_rows, a.aud_seats_per_row ORDER BY total_tickets DESC"
        
        result = database.execute_safe(query, tuple(params) if params else None)
        
        auditoriums_data = []
        if result:
            for row in result:
                occupancy_rate = 0.0
                if row["total_capacity"] and row["total_capacity"] > 0:
                    occupancy_rate = round((row["total_tickets"] * 100.0 / row["total_capacity"]), 2)
                
                auditoriums_data.append({
                    "auditorium_id": row["aud_id"],
                    "auditorium_name": row["aud_name"],
                    "total_capacity": row["total_capacity"],
                    "total_tickets_sold": row["total_tickets"],
                    "total_revenue": float(row["total_revenue"]),
                    "occupancy_rate": occupancy_rate
                })
        
        return {
            "auditoriums": auditoriums_data,
            "start_date": start_date,
            "end_date": end_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener boletos por sala: {str(e)}")

@router.get("/movies/most-sold")
async def get_most_sold_movie(
    start_date: Optional[date] = Query(None, description="Fecha de inicio"),
    end_date: Optional[date] = Query(None, description="Fecha de fin")
):
    """
    g) Consulta de la película más vendida
    """
    try:
        query = """
        SELECT 
            m.mov_id,
            m.mov_title,
            m.mov_genre,
            m.mov_classification,
            m.mov_duration,
            COUNT(s.sal_tic_id) as total_tickets,
            COALESCE(SUM(s.sal_total_amount), 0) as total_revenue
        FROM tb_movie m
        LEFT JOIN tb_screening sc ON m.mov_id = sc.scr_mov_id
        LEFT JOIN tb_sale s ON sc.scr_id = (
            SELECT t.tic_scr_id 
            FROM tb_ticket t 
            WHERE t.tic_id = s.sal_tic_id
        )
        WHERE s.sal_status = 'completed'
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(s.sal_created) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(s.sal_created) <= %s"
            params.append(end_date)
        
        query += """
        GROUP BY m.mov_id, m.mov_title, m.mov_genre, m.mov_classification, m.mov_duration
        HAVING COUNT(s.sal_tic_id) > 0
        ORDER BY total_tickets DESC
        LIMIT 1
        """
        
        result = database.execute_safe(query, tuple(params) if params else None)
        
        if result and len(result) > 0:
            movie = result[0]
            return {
                "movie": {
                    "movie_id": movie["mov_id"],
                    "movie_title": movie["mov_title"],
                    "movie_genre": movie["mov_genre"],
                    "movie_classification": movie["mov_classification"],
                    "movie_duration": movie["mov_duration"],
                    "total_tickets_sold": movie["total_tickets"],
                    "total_revenue": float(movie["total_revenue"])
                },
                "start_date": start_date,
                "end_date": end_date
            }
        
        return {
            "movie": None,
            "message": "No se encontraron ventas en el período especificado",
            "start_date": start_date,
            "end_date": end_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener película más vendida: {str(e)}")

@router.get("/movies/least-sold")
async def get_least_sold_movie(
    start_date: Optional[date] = Query(None, description="Fecha de inicio"),
    end_date: Optional[date] = Query(None, description="Fecha de fin")
):
    """
    h) Consulta de la película menos vendida
    """
    try:
        query = """
        SELECT 
            m.mov_id,
            m.mov_title,
            m.mov_genre,
            m.mov_classification,
            m.mov_duration,
            COUNT(s.sal_tic_id) as total_tickets,
            COALESCE(SUM(s.sal_total_amount), 0) as total_revenue
        FROM tb_movie m
        LEFT JOIN tb_screening sc ON m.mov_id = sc.scr_mov_id
        LEFT JOIN tb_sale s ON sc.scr_id = (
            SELECT t.tic_scr_id 
            FROM tb_ticket t 
            WHERE t.tic_id = s.sal_tic_id
        )
        WHERE (s.sal_status = 'completed' OR s.sal_status IS NULL)
        AND m.mov_status = 'active'
        """
        
        params = []
        
        if start_date:
            query += " AND (s.sal_created IS NULL OR DATE(s.sal_created) >= %s)"
            params.append(start_date)
        
        if end_date:
            query += " AND (s.sal_created IS NULL OR DATE(s.sal_created) <= %s)"
            params.append(end_date)
        
        query += """
        GROUP BY m.mov_id, m.mov_title, m.mov_genre, m.mov_classification, m.mov_duration
        ORDER BY total_tickets ASC, m.mov_title ASC
        LIMIT 1
        """
        
        result = database.execute_safe(query, tuple(params) if params else None)
        
        if result and len(result) > 0:
            movie = result[0]
            return {
                "movie": {
                    "movie_id": movie["mov_id"],
                    "movie_title": movie["mov_title"],
                    "movie_genre": movie["mov_genre"],
                    "movie_classification": movie["mov_classification"],
                    "movie_duration": movie["mov_duration"],
                    "total_tickets_sold": movie["total_tickets"],
                    "total_revenue": float(movie["total_revenue"])
                },
                "start_date": start_date,
                "end_date": end_date
            }
        
        return {
            "movie": None,
            "message": "No se encontraron películas activas",
            "start_date": start_date,
            "end_date": end_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener película menos vendida: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_summary(
    start_date: Optional[date] = Query(None, description="Fecha de inicio"),
    end_date: Optional[date] = Query(None, description="Fecha de fin")
):
    """
    Resumen general de todas las estadísticas principales
    """
    try:
        # Obtener todas las estadísticas en paralelo sería ideal, pero por simplicidad las haremos secuenciales
        
        # Total de ventas
        total_sales_query = """
        SELECT 
            COUNT(*) as total_sales,
            COALESCE(SUM(sal_total_amount), 0) as total_amount
        FROM tb_sale s
        WHERE s.sal_status = 'completed'
        """
        
        # Total de clientes
        customers_query = """
        SELECT COUNT(DISTINCT s.sal_usr_id) as total_customers
        FROM tb_sale s
        WHERE s.sal_status = 'completed'
        AND s.sal_usr_id IS NOT NULL
        """
        
        # Total de boletos
        tickets_query = """
        SELECT COUNT(s.sal_tic_id) as total_tickets
        FROM tb_sale s
        WHERE s.sal_status = 'completed'
        """
        
        params = []
        date_filter = ""
        
        if start_date:
            date_filter += " AND DATE(s.sal_created) >= %s"
            params.append(start_date)
        
        if end_date:
            date_filter += " AND DATE(s.sal_created) <= %s"
            params.append(end_date)
        
        # Ejecutar queries
        total_sales_result = database.execute_safe(total_sales_query + date_filter, tuple(params) if params else None)
        customers_result = database.execute_safe(customers_query + date_filter, tuple(params) if params else None)
        tickets_result = database.execute_safe(tickets_query + date_filter, tuple(params) if params else None)
        
        return {
            "summary": {
                "total_sales_count": total_sales_result[0]["total_sales"] if total_sales_result else 0,
                "total_sales_amount": float(total_sales_result[0]["total_amount"]) if total_sales_result else 0.0,
                "total_customers": customers_result[0]["total_customers"] if customers_result else 0,
                "total_tickets": tickets_result[0]["total_tickets"] if tickets_result else 0
            },
            "period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resumen del dashboard: {str(e)}")

@router.get("/movies/top-selling")
async def get_top_selling_movies(limit: int = Query(5, ge=1, le=10)):
    """
    Obtener las películas más vendidas
    """
    try:
        query = """
        SELECT 
            m.mov_id,
            m.mov_title,
            m.mov_genre,
            COUNT(t.tic_id) as total_tickets,
            COALESCE(SUM(t.tic_price), 0) as total_revenue
        FROM tb_movie m
        LEFT JOIN tb_screening scr ON m.mov_id = scr.scr_mov_id
        LEFT JOIN tb_ticket t ON scr.scr_id = t.tic_scr_id
        WHERE m.mov_status = 'active'
        GROUP BY m.mov_id, m.mov_title, m.mov_genre
        ORDER BY total_tickets DESC
        LIMIT %s
        """
        
        result = database.execute_safe(query, (limit,))
        
        movies = []
        if result:
            for row in result:
                movies.append({
                    "mov_id": row["mov_id"],
                    "mov_title": row["mov_title"],
                    "mov_genre": row["mov_genre"],
                    "total_tickets": row["total_tickets"],
                    "total_revenue": float(row["total_revenue"]) if row["total_revenue"] else 0.0
                })
        
        return {
            "movies": movies,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener películas más vendidas: {str(e)}")

@router.get("/movies/least-selling")
async def get_least_selling_movies(limit: int = Query(5, ge=1, le=10)):
    """
    Obtener las películas menos vendidas
    """
    try:
        query = """
        SELECT 
            m.mov_id,
            m.mov_title,
            m.mov_genre,
            COUNT(t.tic_id) as total_tickets,
            COALESCE(SUM(t.tic_price), 0) as total_revenue
        FROM tb_movie m
        LEFT JOIN tb_screening scr ON m.mov_id = scr.scr_mov_id
        LEFT JOIN tb_ticket t ON scr.scr_id = t.tic_scr_id
        WHERE m.mov_status = 'active'
        GROUP BY m.mov_id, m.mov_title, m.mov_genre
        ORDER BY total_tickets ASC
        LIMIT %s
        """
        
        result = database.execute_safe(query, (limit,))
        
        movies = []
        if result:
            for row in result:
                movies.append({
                    "mov_id": row["mov_id"],
                    "mov_title": row["mov_title"],
                    "mov_genre": row["mov_genre"],
                    "total_tickets": row["total_tickets"],
                    "total_revenue": float(row["total_revenue"]) if row["total_revenue"] else 0.0
                })
        
        return {
            "movies": movies,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener películas menos vendidas: {str(e)}")
