"""
Product model using Pydantic for validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from bson import ObjectId
from datetime import datetime


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# ================= BASE ================= #

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    available: bool = True
    gender: Literal["men", "women"]
    description: Optional[str] = Field(None, max_length=1000)


# ================= CREATE ================= #

class ProductCreate(ProductBase):
    pass


# ================= DB MODEL ================= #

class Product(ProductBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ================= RESPONSE ================= #

class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    available: bool
    gender: Literal["men", "women"]
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
