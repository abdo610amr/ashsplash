"""
Order routes for handling order-related API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.order import OrderCreateInput, OrderResponse, OrderItem, OrderCreate
from app.database import get_database
from app.auth import verify_admin_key
from app.services.notify import send_order_notification
from app.services.order_service import update_order_status_service
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_input: OrderCreateInput):
    """
    Create a new order (public endpoint).
    
    Server-side validation and calculation:
    - Validates products exist and are available
    - Fetches prices from database
    - Calculates total server-side
    - Sets status to "pending"
    - Sends notification to Telegram admin bot
    
    Args:
        order_input: Order input data (customer, items with product_id and quantity only)
        
    Returns:
        Created order with server-calculated values
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not available"
            )
        
        products_collection = db.products
        validated_items = []
        total = 0.0
        unavailable_products = []
        product_cache = {}  # Cache products to avoid duplicate lookups
        
        # Validate all products first
        for item in order_input.items:
            if not ObjectId.is_valid(item.product_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid product ID format: {item.product_id}"
                )
            
            product = await products_collection.find_one({"_id": ObjectId(item.product_id)})
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product not found: {item.product_id}"
                )
            
            # Cache product for later use
            product_cache[item.product_id] = product
            
            # Validate availability
            if not product.get("available", False):
                unavailable_products.append(product.get("name", item.product_id))
        
        # Abort if any products are unavailable
        if unavailable_products:
            product_names = ", ".join(unavailable_products)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product(s) not available: {product_names}"
            )
        
        # All products are available - build validated items and calculate total
        for item in order_input.items:
            product = product_cache[item.product_id]
            product_price = product.get("price", 0.0)
            
            if product_price <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product has invalid price: {item.product_id}"
                )
            
            # Build validated order item with server-fetched price
            validated_items.append(OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price=product_price
            ))
            
            # Calculate total
            total += product_price * item.quantity
        
        # Build complete order with server-calculated values
        # Use .dict() for Pydantic v1 compatibility, .model_dump() for v2
        customer_dict = order_input.customer.dict() if hasattr(order_input.customer, 'dict') else order_input.customer.model_dump()
        items_dict = [item.dict() if hasattr(item, 'dict') else item.model_dump() for item in validated_items]
        
        order_data = {
            "customer": customer_dict,
            "items": items_dict,
            "total": total,
            "status": "pending",  # Force default status
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save order to database
        orders_collection = db.orders
        result = await orders_collection.insert_one(order_data)
        order_data["_id"] = result.inserted_id
        order_data["id"] = str(result.inserted_id)
        
        # Send notification to Telegram admin with server-calculated values
        await send_order_notification(order_data)
        
        return OrderResponse(**order_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def get_order(order_id: str):
    """
    Get a single order by ID.
    
    Args:
        order_id: Order ID
        
    Returns:
        Order details
    """
    try:
        if not ObjectId.is_valid(order_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid order ID format"
            )
        
        db = get_database()
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not available"
            )
        
        orders_collection = db.orders
        order = await orders_collection.find_one({"_id": ObjectId(order_id)})
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order["id"] = str(order["_id"])
        return OrderResponse(**order)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching order: {str(e)}"
        )


@router.patch("/{order_id}/status", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def update_order_status(
    order_id: str,
    new_status: str,
    _: bool = Depends(verify_admin_key)
):
    """
    Update order status (admin only - requires X-ADMIN-KEY header).
    
    Args:
        order_id: Order ID
        new_status: New status (pending, confirmed, shipped, delivered, cancelled)
        _: Admin key verification (from dependency)
        
    Returns:
        Updated order
    """
    try:
        return await update_order_status_service(order_id, new_status)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating order status: {str(e)}"
        )

