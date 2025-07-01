from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from models.sale import Sale, SaleCreate, SaleUpdate, PaymentMethod
from models.ticket import TicketCreate
from services.sale_service import SaleService
from services.ticket_service import TicketService
from services.user_service import UserService
import tempfile
import uuid

router = APIRouter(tags=["sales"])
sale_service = SaleService()

@router.post("/", response_model=Sale)
def create_sale(sale: SaleCreate):
    """Create a new sale"""
    try:
        return sale_service.create_sale(sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Sale])
def get_all_sales():
    """Get all sales"""
    try:
        return sale_service.get_all_sales()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{sale_id}", response_model=Sale)
def get_sale(sale_id: int):
    """Get a specific sale by ID"""
    try:
        sale = sale_service.get_sale_by_id(sale_id)
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{sale_id}", response_model=Sale)
def update_sale(sale_id: int, sale_update: SaleUpdate):
    """Update a sale"""
    try:
        updated_sale = sale_service.update_sale(sale_id, sale_update)
        if not updated_sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        return updated_sale
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{sale_id}")
def delete_sale(sale_id: int):
    """Delete a sale"""
    try:
        success = sale_service.delete_sale(sale_id)
        if not success:
            raise HTTPException(status_code=404, detail="Sale not found")
        return {"message": "Sale deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employee/{employee_id}", response_model=List[Sale])
def get_sales_by_employee(employee_id: int):
    """Get all sales by a specific employee"""
    try:
        return sale_service.get_sales_by_employee(employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=List[Sale])
def get_sales_by_user(user_id: int):
    """Get all sales for a specific user"""
    try:
        return sale_service.get_sales_by_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/date/{sale_date}", response_model=List[Sale])
def get_sales_by_date(sale_date: date):
    """Get all sales for a specific date"""
    try:
        return sale_service.get_sales_by_date(sale_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/date-range/")
def get_sales_by_date_range(start_date: date, end_date: date):
    """Get all sales within a date range"""
    try:
        sales = sale_service.get_sales_by_date_range(start_date, end_date)
        return sales
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/daily/{sale_date}")
def get_daily_statistics(sale_date: date):
    """Get daily sales statistics"""
    try:
        stats = sale_service.get_daily_statistics(sale_date)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/employee/{employee_id}")
def get_employee_statistics(employee_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """Get sales statistics for a specific employee"""
    try:
        stats = sale_service.get_employee_statistics(employee_id, start_date, end_date)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete/{sale_id}")
def complete_sale(sale_id: int):
    """Complete a sale (process tickets)"""
    try:
        success = sale_service.complete_sale(sale_id)
        if not success:
            raise HTTPException(status_code=404, detail="Sale not found or already completed")
        return {"message": "Sale completed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PurchaseRequest(BaseModel):
    customer_email: str
    customer_name: str
    customer_phone: Optional[str] = None
    scr_id: str
    seats: List[str]  # Lista de asientos como ["A1", "A2", "B5"]
    payment_method: PaymentMethod = PaymentMethod.CASH
    total_amount: float

@router.post("/purchase")
async def create_purchase(purchase: PurchaseRequest):
    """Create a complete purchase with tickets and sale record, return PDF"""
    try:
        ticket_service = TicketService()
        user_service = UserService()
        
        # 1. Verificar o crear usuario
        user = user_service.get_user_by_email(purchase.customer_email)
        if not user:
            # Crear usuario básico
            from models.user import UserCreate
            user_data = UserCreate(
                usr_name=purchase.customer_name,
                usr_email=purchase.customer_email,
                usr_phone=purchase.customer_phone or "",
                usr_password="temp123",  # Password temporal
                usr_role="customer"
            )
            user = user_service.create_user(user_data)
        
        # 2. Crear tickets para cada asiento
        ticket_ids = []
        for seat in purchase.seats:
            # Parsear asiento (ej: "A1" -> row="A", seat=1)
            row = seat[0]
            seat_number = int(seat[1:])
            
            ticket_data = TicketCreate(
                tic_scr_id=purchase.scr_id,
                tic_row=row,
                tic_seat=seat_number,
                tic_price=purchase.total_amount / len(purchase.seats),
                tic_status="sold"
            )
            
            ticket = ticket_service.create_ticket(ticket_data)
            ticket_ids.append(ticket.tic_id)
        
        # 3. Crear la venta (usar primer ticket como referencia)
        sale_data = SaleCreate(
            sal_usr_id=user.usr_id,
            sal_emp_id="emp_default",  # Empleado por defecto para ventas online
            sal_tic_id=ticket_ids[0],  # Primer ticket como referencia
            sal_total_amount=purchase.total_amount,
            sal_payment_method=purchase.payment_method,
            sal_status="completed"
        )
        
        sale = sale_service.create_sale(sale_data)
        
        # 4. Generar PDF del boleto
        pdf_path = await generate_ticket_pdf(sale, purchase, ticket_ids)
        
        return {
            "success": True,
            "sale_id": sale.sal_id,
            "ticket_ids": ticket_ids,
            "pdf_url": f"/sales/download-ticket/{sale.sal_id}",
            "message": "Compra realizada exitosamente"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing purchase: {str(e)}")

@router.get("/download-ticket/{sale_id}")
async def download_ticket(sale_id: str):
    """Download ticket PDF for a sale"""
    try:
        # Obtener datos de la venta
        sale = sale_service.get_sale_by_id(sale_id)
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        
        # Generar o recuperar PDF
        pdf_path = f"/tmp/ticket_{sale_id}.pdf"
        
        # Si el archivo no existe, regenerarlo
        import os
        if not os.path.exists(pdf_path):
            # Recrear PDF basado en los datos de la venta
            pdf_path = await regenerate_ticket_pdf(sale)
        
        return FileResponse(
            path=pdf_path,
            filename=f"ticket_{sale_id}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_ticket_pdf(sale, purchase_data, ticket_ids):
    """Generate PDF ticket with purchase details"""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    import tempfile
    import os
    
    # Crear archivo temporal
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f"ticket_{sale.sal_id}.pdf")
    
    # Crear PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 100, "🎬 Cinema el Foraneo")
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 140, "BOLETO DE ENTRADA")
    
    # Línea separadora
    c.line(50, height - 160, width - 50, height - 160)
    
    # Información del boleto
    y_pos = height - 200
    c.setFont("Helvetica-Bold", 12)
    
    # Obtener información de la función desde la base de datos
    from services.screening_service import ScreeningService
    from services.movie_service import MovieService
    
    screening_service = ScreeningService()
    movie_service = MovieService()
    
    screening = screening_service.get_screening_by_id(purchase_data.scr_id)
    movie = movie_service.get_movie_by_id(screening.scr_mov_id) if screening else None
    
    # Datos de la película y función
    if movie and screening:
        c.drawString(50, y_pos, f"Película: {movie.mov_title}")
        y_pos -= 25
        c.drawString(50, y_pos, f"Función: {screening.scr_start_time}")
        y_pos -= 25
        c.drawString(50, y_pos, f"Sala: {screening.aud_name or 'N/A'}")
        y_pos -= 25
    
    # Asientos
    seats_str = ", ".join(purchase_data.seats)
    c.drawString(50, y_pos, f"Asientos: {seats_str}")
    y_pos -= 25
    
    # Cliente
    c.drawString(50, y_pos, f"Cliente: {purchase_data.customer_name}")
    y_pos -= 25
    c.drawString(50, y_pos, f"Email: {purchase_data.customer_email}")
    y_pos -= 25
    
    # Total
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos - 20, f"Total: ${purchase_data.total_amount:.2f} MXN")
    
    # ID de venta
    c.setFont("Helvetica", 10)
    c.drawString(50, y_pos - 50, f"ID de Venta: {sale.sal_id}")
    c.drawString(50, y_pos - 65, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 50, "Conserve este boleto para ingresar a la función.")
    c.drawString(50, 35, "No se admiten devoluciones ni cambios.")
    
    c.save()
    return pdf_path

async def regenerate_ticket_pdf(sale):
    """Regenerate PDF from sale data"""
    # Esta función sería similar a generate_ticket_pdf pero obteniendo
    # los datos desde la base de datos usando el sale_id
    # Por simplicidad, retornar path temporal
    return f"/tmp/ticket_{sale.sal_id}.pdf"
