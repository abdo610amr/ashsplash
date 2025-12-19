"""
Order service functions for business logic.
Can be called directly by bot or via routes with auth.
"""
from fastapi import HTTPException, status
from app.models.order import OrderResponse
from app.database import get_database
from bson import ObjectId
from datetime import datetime


async def update_order_status_service(order_id: str, new_status: str) -> OrderResponse:
    """
    Update order status (internal service function).
    
    Args:
        order_id: Order ID
        new_status: New status (pending, confirmed, shipped, delivered, cancelled)
        
    Returns:
        Updated order
    """
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    orders_collection = db.orders
    result = await orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Fetch updated order
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    order["id"] = str(order["_id"])
    
    return OrderResponse(**order)

