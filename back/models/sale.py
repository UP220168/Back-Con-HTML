from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    DIGITAL = "digital"

class SaleStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Sale(BaseModel):
    sal_id: str
    sal_usr_id: str = Field(..., description="ID del usuario")
    sal_emp_id: str = Field(..., description="ID del empleado")
    sal_tic_id: str = Field(..., description="ID del ticket")
    sal_total_amount: float = Field(..., gt=0, description="Monto total")
    sal_payment_method: PaymentMethod = Field(..., description="Método de pago")
    sal_status: SaleStatus = Field(default=SaleStatus.PENDING)
    sal_created: Optional[datetime] = None
    sal_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    sal_usr_id: str = Field(..., description="ID del usuario")
    sal_emp_id: str = Field(..., description="ID del empleado")
    sal_tic_id: str = Field(..., description="ID del ticket")
    sal_total_amount: float = Field(..., gt=0, description="Monto total")
    sal_payment_method: PaymentMethod = Field(..., description="Método de pago")
    sal_status: Optional[SaleStatus] = SaleStatus.PENDING

class SaleUpdate(BaseModel):
    sal_usr_id: Optional[str] = None
    sal_emp_id: Optional[str] = None
    sal_tic_id: Optional[str] = None
    sal_total_amount: Optional[float] = Field(None, gt=0)
    sal_payment_method: Optional[PaymentMethod] = None
    sal_status: Optional[SaleStatus] = None

class SaleResponse(BaseModel):
    sal_id: str
    sal_usr_id: str
    sal_emp_id: str
    sal_tic_id: str
    sal_total_amount: float
    sal_payment_method: PaymentMethod
    sal_status: SaleStatus
    sal_created: Optional[datetime] = None
    sal_updated: Optional[datetime] = None

    @classmethod
    def from_sale(cls, sale: Sale) -> "SaleResponse":
        return cls(**sale.model_dump())
