from pydantic import BaseModel
from decimal import Decimal
from typing import List

class SalesTrendItem(BaseModel):
    date: str
    total_sales: Decimal

class SalesTrendResponse(BaseModel):
    data: List[SalesTrendItem]

class InventoryValuationItem(BaseModel):
    category_name: str
    total_value: Decimal

class InventoryValuationResponse(BaseModel):
    data: List[InventoryValuationItem]

class CashFlowItem(BaseModel):
    date: str
    money_in: Decimal
    money_out: Decimal

class CashFlowResponse(BaseModel):
    data: List[CashFlowItem]
