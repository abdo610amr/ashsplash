"""
Review model using Pydantic for validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime
from app.models.product import PyObjectId


class ReviewCreate(BaseModel):
    """Schema for creating a review."""
    product_id: str = Field(..., description="Product ID")
    name: str = Field(..., min_length=1, max_length=100, description="Reviewer name")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment")


class Review(BaseModel):
    """Review model with ID and timestamps."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    product_id: str
    name: str
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "product_id": "507f1f77bcf86cd799439011",
                "name": "John Doe",
                "rating": 5,
                "comment": "Excellent product! Highly recommended."
            }
        }


class ReviewResponse(BaseModel):
    """Review response schema for API."""
    id: str
    product_id: str
    name: str
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

