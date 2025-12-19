"""
Order model using Pydantic for validation.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.models.product import PyObjectId


class OrderItemInput(BaseModel):
    """Order item input schema (client sends only product_id and quantity)."""
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity of items")


class OrderItem(BaseModel):
    """Order item schema (server includes price)."""
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity of items")
    price: float = Field(..., gt=0, description="Price per item")


class CustomerInfo(BaseModel):
    """Customer information schema."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    address: str = Field(..., min_length=1, max_length=500)


class OrderCreateInput(BaseModel):
    """Input schema for creating an order (client sends minimal data)."""
    customer: CustomerInfo
    items: List[OrderItemInput] = Field(..., min_items=1)


class OrderBase(BaseModel):
    """Base order schema."""
    customer: CustomerInfo
    items: List[OrderItem] = Field(..., min_items=1)
    total: float = Field(..., gt=0)
    status: str = Field(default="pending", description="Order status: pending, confirmed, shipped, delivered, cancelled")


class OrderCreate(OrderBase):
    """Schema for creating an order."""
    pass


class Order(OrderBase):
    """Order model with ID and timestamps."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "customer": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1234567890",
                    "address": "123 Main St, City, Country"
                },
                "items": [
                    {
                        "product_id": "507f1f77bcf86cd799439011",
                        "quantity": 2,
                        "price": 99.99
                    }
                ],
                "total": 199.98,
                "status": "pending"
            }
        }


class OrderResponse(BaseModel):
    """Order response schema for API."""
    id: str
    customer: CustomerInfo
    items: List[OrderItem]
    total: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

