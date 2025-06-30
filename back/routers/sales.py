from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, date
from models.sale import Sale, SaleCreate, SaleUpdate
from services.sale_service import SaleService

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
