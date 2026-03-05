import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PartOut(BaseModel):
    id: uuid.UUID
    sku: str
    name: str
    brand: str
    category: str
    vehicle_compat: str
    active: bool
    suggested_price: Optional[str] = None


class PartOfferOut(BaseModel):
    supplier_id: uuid.UUID
    supplier_name: str
    price: str
    availability_status: str
    lead_time_days: Optional[int] = None
    supplier_sku: Optional[str] = None


class CartItemOut(BaseModel):
    id: uuid.UUID
    part_id: uuid.UUID
    sku: str
    name: str
    brand: str
    category: str
    qty: int
    chosen_supplier_id: Optional[uuid.UUID] = None
    chosen_supplier_name: Optional[str] = None
    unit_price_snapshot: str


class CartOut(BaseModel):
    id: uuid.UUID
    status: str
    items: list[CartItemOut]
    created_at: datetime
    updated_at: datetime


class AddCartItemIn(BaseModel):
    part_id: uuid.UUID
    qty: int = Field(default=1, ge=1, le=999)
    chosen_supplier_id: Optional[uuid.UUID] = None
    unit_price_snapshot: Optional[str] = None


class CheckoutFromCartIn(BaseModel):
    supplier_id: uuid.UUID
    delivery_mode: str = Field(default="delivery", min_length=3, max_length=20)
    delivery_address: Optional[str] = Field(default=None, max_length=500)
    shipping: str = Field(default="0.00", max_length=20)
    discount: str = Field(default="0.00", max_length=20)


class PurchaseOrderItemOut(BaseModel):
    id: uuid.UUID
    part_id: uuid.UUID
    sku: str
    name: str
    qty: int
    unit_price: str
    total_price: str


class PurchaseOrderOut(BaseModel):
    id: uuid.UUID
    order_number: str
    status: str
    supplier_id: uuid.UUID
    supplier_name: str
    subtotal: str
    shipping: str
    discount: str
    total: str
    delivery_mode: str
    delivery_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: list[PurchaseOrderItemOut]


class PurchaseOrderStatusUpdate(BaseModel):
    status: str = Field(min_length=3, max_length=20)