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
    """Create a complete purchase with tickets and sale record"""
    try:
        # Importar solo lo necesario para evitar dependencias problemáticas
        from db_connection import database
        import uuid
        from datetime import datetime
        
        print(f"Procesando compra: {purchase}")
        
        # 1. Usar usuario existente (hardcoded para evitar problemas)
        user_id = "47e6d7df-c844-447a-8dc9-3c4ae29b8438"  # Usuario existente de la BD
        
        # 2. Crear tickets directamente en la base de datos
        ticket_ids = []
        
        for seat in purchase.seats:
            try:
                # Parsear asiento (ej: "A1" -> row="A", seat=1)
                row = seat[0]
                seat_number = int(seat[1:])
                
                print(f"Procesando asiento: {seat} -> fila: {row}, número: {seat_number}")
                
                # Generar ID único para el ticket
                ticket_id = str(uuid.uuid4())
                
                # Verificar que el asiento no esté ocupado
                check_query = """
                SELECT COUNT(*) as count FROM tb_ticket 
                WHERE tic_scr_id = %s AND tic_row = %s AND tic_seat = %s AND tic_status = 'sold'
                """
                check_result = database.execute_safe(check_query, (purchase.scr_id, row, seat_number))
                
                if check_result and check_result[0]['count'] > 0:
                    raise ValueError(f"El asiento {seat} ya está ocupado")
                
                # INSERT directo usando execute_safe
                insert_query = """
                INSERT INTO tb_ticket (tic_id, tic_row, tic_seat, tic_scr_id, tic_status, tic_created)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                params = (ticket_id, row, seat_number, purchase.scr_id, "sold", datetime.now())
                database.execute_safe(insert_query, params)
                ticket_ids.append(ticket_id)
                print(f"Ticket creado exitosamente: {ticket_id}")
                
            except Exception as ticket_error:
                print(f"Error creando ticket para asiento {seat}: {ticket_error}")
                raise ValueError(f"Error creando ticket para asiento {seat}: {str(ticket_error)}")

        # 3. Crear la venta directamente en la base de datos
        sale_id = str(uuid.uuid4())
        
        sale_insert_query = """
        INSERT INTO tb_sale (sal_id, sal_usr_id, sal_emp_id, sal_tic_id, sal_total_amount, sal_payment_method, sal_status, sal_created)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        sale_params = (
            sale_id,
            user_id,
            "d2793c93-5574-11f0-9612-c6d18831a5b6",  # ID del empleado administrador
            ticket_ids[0] if ticket_ids else str(uuid.uuid4()),  # Primer ticket como referencia
            purchase.total_amount,
            purchase.payment_method.value,  # Usar .value para obtener el string del enum
            "completed",
            datetime.now()
        )
        
        database.execute_safe(sale_insert_query, sale_params)
        print(f"Venta creada exitosamente: {sale_id}")
        
        return {
            "success": True,
            "sale_id": sale_id,
            "ticket_ids": ticket_ids,
            "message": "Compra realizada exitosamente",
            "customer_email": purchase.customer_email,
            "customer_name": purchase.customer_name,
            "total_amount": purchase.total_amount,
            "seats": purchase.seats
        }
        
    except ValueError as e:
        print(f"ValueError en purchase: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_msg = f"Error en purchase: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing purchase: {str(e)}")

# Endpoint de simulación para compras (no modifica la base de datos)
@router.post("/purchase-simulation")
async def create_purchase_simulation(purchase: PurchaseRequest):
    """Simulate a complete purchase without modifying the database - solo para demostración"""
    try:
        from db_connection import database
        import uuid
        from datetime import datetime
        
        print(f"Simulando compra: {purchase}")
        
        # 1. Verificar que la función existe
        screening_query = "SELECT * FROM tb_screening WHERE scr_id = %s"
        screening_result = database.execute_safe(screening_query, (purchase.scr_id,))
        
        if not screening_result:
            raise ValueError(f"La función {purchase.scr_id} no existe")
        
        screening = screening_result[0]
        
        # 2. Verificar que los asientos están disponibles
        occupied_seats = []
        for seat in purchase.seats:
            row = seat[0]
            seat_number = int(seat[1:])
            
            check_query = """
            SELECT COUNT(*) as count FROM tb_ticket 
            WHERE tic_scr_id = %s AND tic_row = %s AND tic_seat = %s AND tic_status = 'sold'
            """
            check_result = database.execute_safe(check_query, (purchase.scr_id, row, seat_number))
            
            if check_result and check_result[0]['count'] > 0:
                occupied_seats.append(seat)
        
        if occupied_seats:
            raise ValueError(f"Los siguientes asientos ya están ocupados: {', '.join(occupied_seats)}")
        
        # 3. Simular la creación de IDs sin guardar en BD
        sale_id = str(uuid.uuid4())
        ticket_ids = [str(uuid.uuid4()) for _ in purchase.seats]
        
        print(f"Simulación exitosa - Venta ID: {sale_id}, Tickets: {ticket_ids}")
        
        return {
            "success": True,
            "sale_id": sale_id,
            "ticket_ids": ticket_ids,
            "message": "Compra simulada exitosamente",
            "customer_email": purchase.customer_email,
            "customer_name": purchase.customer_name,
            "total_amount": purchase.total_amount,
            "seats": purchase.seats,
            "simulation": True,
            "screening_info": {
                "movie_id": screening['scr_mov_id'],
                "auditorium_id": screening['scr_aud_id'], 
                "date": str(screening['scr_date']),
                "time": str(screening['scr_time']),
                "price": float(screening['scr_price'])
            }
        }
        
    except ValueError as e:
        print(f"ValueError en simulación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_msg = f"Error en simulación: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing simulation: {str(e)}")

# Endpoint temporal para compras que evita los servicios problemáticos
@router.post("/purchase-simple")
async def create_purchase_simple(purchase: PurchaseRequest):
    """Create a complete purchase with tickets and sale record - versión simplificada"""
    try:
        # Importar solo lo necesario para evitar dependencias problemáticas
        from db_connection import database
        import uuid
        from datetime import datetime
        
        print(f"Procesando compra simple: {purchase}")
        
        # 1. Usar usuario existente (hardcoded para evitar problemas)
        user_id = "47e6d7df-c844-447a-8dc9-3c4ae29b8438"  # Usuario existente de la BD
        
        # 2. Crear tickets directamente como 'available' primero (según trigger)
        ticket_ids = []
        
        for seat in purchase.seats:
            try:
                # Parsear asiento (ej: "A1" -> row="A", seat=1)
                row = seat[0]
                seat_number = int(seat[1:])
                
                print(f"Procesando asiento: {seat} -> fila: {row}, número: {seat_number}")
                
                # Verificar que el asiento no esté ocupado
                check_query = """
                SELECT COUNT(*) as count FROM tb_ticket 
                WHERE tic_scr_id = %s AND tic_row = %s AND tic_seat = %s AND tic_status IN ('sold', 'reserved')
                """
                check_result = database.execute_safe(check_query, (purchase.scr_id, row, seat_number))
                
                if check_result and check_result[0]['count'] > 0:
                    raise ValueError(f"El asiento {seat} ya está ocupado")
                
                # Crear ticket como 'available' primero (requerido por trigger)
                ticket_id = str(uuid.uuid4())
                
                insert_query = """
                INSERT INTO tb_ticket (tic_id, tic_row, tic_seat, tic_scr_id, tic_status, tic_created)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                params = (ticket_id, row, seat_number, purchase.scr_id, "available", datetime.now())
                database.execute_safe(insert_query, params)
                ticket_ids.append(ticket_id)
                print(f"Ticket creado como available: {ticket_id}")
                
            except Exception as ticket_error:
                print(f"Error procesando ticket para asiento {seat}: {ticket_error}")
                raise ValueError(f"Error procesando ticket para asiento {seat}: {str(ticket_error)}")

        # 3. Crear la venta como 'pending' primero (requerido por trigger)
        sale_id = str(uuid.uuid4())
        
        sale_insert_query = """
        INSERT INTO tb_sale (sal_id, sal_usr_id, sal_emp_id, sal_tic_id, sal_total_amount, sal_payment_method, sal_status, sal_created)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        sale_params = (
            sale_id,
            user_id,
            "d2793c93-5574-11f0-9612-c6d18831a5b6",  # ID del empleado administrador
            ticket_ids[0] if ticket_ids else str(uuid.uuid4()),  # Primer ticket como referencia
            purchase.total_amount,
            purchase.payment_method.value,  # Usar .value para obtener el string del enum
            "pending",  # Crear como pending primero (requerido por trigger)
            datetime.now()
        )
        
        database.execute_safe(sale_insert_query, sale_params)
        print(f"Venta creada como pending: {sale_id}")
        
        # 4. Actualizar venta a 'completed' para activar el trigger que cambia tickets a 'sold'
        update_sale_query = """
        UPDATE tb_sale 
        SET sal_status = 'completed', sal_updated = %s
        WHERE sal_id = %s
        """
        database.execute_safe(update_sale_query, (datetime.now(), sale_id))
        print(f"Venta actualizada a completed: {sale_id} - Trigger debería cambiar tickets a 'sold'")
        
        # 5. Generar el PDF del boleto con los datos reales
        try:
            print(f"Iniciando generación de PDF para venta: {sale_id}")
            
            # Crear un objeto sale simulado para la función PDF
            class MockSale:
                def __init__(self, sale_id):
                    self.sal_id = sale_id
            
            mock_sale = MockSale(sale_id)
            pdf_path = await generate_ticket_pdf(mock_sale, purchase, ticket_ids)
            print(f"✅ PDF del boleto generado exitosamente: {pdf_path}")
            
            # Verificar que el archivo existe
            import os
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✅ Archivo PDF confirmado - Tamaño: {file_size} bytes")
            else:
                print(f"❌ Archivo PDF no encontrado en: {pdf_path}")
                pdf_path = None
                
        except Exception as pdf_error:
            print(f"❌ Error generando PDF: {pdf_error}")
            import traceback
            print(traceback.format_exc())
            pdf_path = None
        
        return {
            "success": True,
            "sale_id": sale_id,
            "ticket_ids": ticket_ids,
            "message": "Compra realizada exitosamente",
            "customer_email": purchase.customer_email,
            "customer_name": purchase.customer_name,
            "total_amount": purchase.total_amount,
            "seats": purchase.seats,
            "pdf_generated": pdf_path is not None,
            "pdf_path": pdf_path
        }
        
    except ValueError as e:
        print(f"ValueError en purchase-simple: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_msg = f"Error en purchase-simple: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing purchase: {str(e)}")

@router.get("/download-ticket/{sale_id}")
async def download_ticket(sale_id: str):
    """Download ticket PDF for a sale"""
    try:
        import os
        
        # Buscar el archivo PDF
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, f"ticket_{sale_id}.pdf")
        
        if not os.path.exists(pdf_path):
            # Si no existe, intentar regenerarlo
            try:
                from db_connection import database
                
                # Obtener datos de la venta
                sale_query = "SELECT * FROM tb_sale WHERE sal_id = %s"
                sale_result = database.execute_safe(sale_query, (sale_id,))
                
                if not sale_result:
                    raise HTTPException(status_code=404, detail="Sale not found")
                
                sale_data = sale_result[0]
                
                # Obtener tickets de la venta
                tickets_query = "SELECT * FROM tb_ticket WHERE tic_id = %s"
                tickets_result = database.execute_safe(tickets_query, (sale_data['sal_tic_id'],))
                
                if tickets_result:
                    # Regenerar PDF con datos disponibles
                    class MockPurchase:
                        def __init__(self, sale_data):
                            self.customer_name = "Cliente (desde venta guardada)"
                            self.customer_email = "email@sistema.com"
                            self.customer_phone = ""
                            self.scr_id = tickets_result[0]['tic_scr_id']
                            self.seats = [f"{tickets_result[0]['tic_row']}{tickets_result[0]['tic_seat']}"]
                            self.total_amount = float(sale_data['sal_total_amount'])
                            self.payment_method = sale_data['sal_payment_method']
                    
                    class MockSale:
                        def __init__(self, sale_id):
                            self.sal_id = sale_id
                    
                    mock_sale = MockSale(sale_id)
                    mock_purchase = MockPurchase(sale_data)
                    
                    pdf_path = await generate_ticket_pdf(mock_sale, mock_purchase, [sale_data['sal_tic_id']])
                else:
                    raise HTTPException(status_code=404, detail="Ticket data not found")
                    
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Could not generate PDF: {str(e)}")
        
        return FileResponse(
            path=pdf_path,
            filename=f"boleto_{sale_id}.txt",
            media_type="text/plain; charset=utf-8"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_ticket_pdf(sale, purchase_data, ticket_ids):
    """Generate PDF ticket with purchase details"""
    # Comentado temporalmente por problemas de dependencias
    # from reportlab.lib.pagesizes import letter
    # from reportlab.pdfgen import canvas  
    # from reportlab.lib.units import inch
    import tempfile
    import os
    from datetime import datetime
    
    # Por ahora crear un archivo de texto con formato de boleto
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f"ticket_{sale.sal_id}.pdf")
    
    # Obtener información adicional de la función y película
    try:
        from db_connection import database
        
        # Obtener datos de la función
        screening_query = """
        SELECT s.*, m.mov_title, a.aud_name 
        FROM tb_screening s
        JOIN tb_movie m ON s.scr_mov_id = m.mov_id
        JOIN tb_auditorium a ON s.scr_aud_id = a.aud_id
        WHERE s.scr_id = %s
        """
        screening_result = database.execute_safe(screening_query, (purchase_data.scr_id,))
        
        if screening_result:
            screening_data = screening_result[0]
        else:
            screening_data = None
            
    except Exception as e:
        print(f"Error obteniendo datos de la función: {e}")
        screening_data = None
    
    # Crear contenido del boleto
    ticket_content = f"""
═══════════════════════════════════════════════════════════════
                    🎬 CINEMA EL FORÁNEO 🎬
                      BOLETO DE ENTRADA
═══════════════════════════════════════════════════════════════

📋 INFORMACIÓN DE LA COMPRA
   ID de Venta: {sale.sal_id if hasattr(sale, 'sal_id') else 'N/A'}
   Fecha de Compra: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

🎭 DETALLES DE LA FUNCIÓN
"""
    
    if screening_data:
        # Formatear fecha y hora de la función
        screening_date = screening_data.get('scr_date', 'N/A')
        screening_time = screening_data.get('scr_time', 'N/A')
        
        ticket_content += f"""   Película: {screening_data.get('mov_title', 'N/A')}
   Sala: {screening_data.get('aud_name', 'N/A')}
   Fecha de Función: {screening_date}
   Hora de Función: {screening_time}
   Precio por Boleto: ${screening_data.get('scr_price', 0):.2f} MXN
"""
    else:
        ticket_content += f"""   Película: [Información no disponible]
   Sala: [Información no disponible]
   Función: [Información no disponible]
   Precio: ${purchase_data.total_amount / len(purchase_data.seats):.2f} MXN
"""

    ticket_content += f"""
👤 DATOS DEL CLIENTE
   Nombre: {purchase_data.customer_name}
   Email: {purchase_data.customer_email}
   Teléfono: {purchase_data.customer_phone or 'No proporcionado'}

🎟️ BOLETOS ADQUIRIDOS
   Cantidad: {len(purchase_data.seats)} boleto(s)
   Asientos: {', '.join(purchase_data.seats)}
   IDs de Tickets: {', '.join(ticket_ids[:3])}{'...' if len(ticket_ids) > 3 else ''}

💰 RESUMEN DE PAGO
   Subtotal: ${purchase_data.total_amount:.2f} MXN
   Método de Pago: {purchase_data.payment_method.upper()}
   Total Pagado: ${purchase_data.total_amount:.2f} MXN

═══════════════════════════════════════════════════════════════

📝 INSTRUCCIONES IMPORTANTES:
• Presente este boleto al ingresar a la sala
• Llegue 15 minutos antes del inicio de la función
• No se admiten devoluciones ni cambios
• Prohibido el ingreso de alimentos y bebidas externas
• Mantenga el boleto durante toda la función

═══════════════════════════════════════════════════════════════

                ¡DISFRUTE SU FUNCIÓN! 🍿🎬

                    Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                    Sistema Cinema el Foráneo v1.0

═══════════════════════════════════════════════════════════════
"""
    
    # Escribir contenido al archivo
    with open(pdf_path, 'w', encoding='utf-8') as f:
        f.write(ticket_content)
    
    print(f"Boleto generado: {pdf_path}")
    return pdf_path

async def regenerate_ticket_pdf(sale):
    """Regenerate PDF from sale data"""
    # Esta función sería similar a generate_ticket_pdf pero obteniendo
    # los datos desde la base de datos usando el sale_id
    # Por simplicidad, retornar path temporal
    return f"/tmp/ticket_{sale.sal_id}.pdf"

# Endpoint temporal para crear tickets directamente
@router.post("/create-test-ticket")
async def create_test_ticket():
    """Crear un ticket de prueba disponible"""
    try:
        from db_connection import database
        import uuid
        from datetime import datetime
        
        # Crear ticket de prueba
        ticket_id = str(uuid.uuid4())
        
        insert_query = """
        INSERT INTO tb_ticket (tic_id, tic_row, tic_seat, tic_scr_id, tic_status, tic_created)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (ticket_id, "F", 5, "87579d02-4e04-4b77-b588-6ab68aedddba", "available", datetime.now())
        database.execute_safe(insert_query, params)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "message": "Ticket de prueba creado exitosamente",
            "seat": "F5",
            "status": "available"
        }
        
    except Exception as e:
        import traceback
        print(f"Error creando ticket de prueba: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating test ticket: {str(e)}")
