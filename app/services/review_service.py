"""
Review service functions for business logic.
"""
from fastapi import HTTPException, status
from app.models.review import ReviewCreate, ReviewResponse
from app.database import get_database
from bson import ObjectId
from datetime import datetime


async def create_review_service(review: ReviewCreate) -> ReviewResponse:
    """
    Create a new review (internal service function).
    
    Args:
        review: Review data
        
    Returns:
        Created review
    """
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Validate product_id format
    if not ObjectId.is_valid(review.product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid product ID format: {review.product_id}"
        )
    
    # Validate that product exists
    products_collection = db.products
    product = await products_collection.find_one({"_id": ObjectId(review.product_id)})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {review.product_id}"
        )
    
    # Create review
    reviews_collection = db.reviews
    # Use .dict() for Pydantic v1 compatibility, .model_dump() for v2
    review_dict = review.dict() if hasattr(review, 'dict') else review.model_dump()
    review_dict["created_at"] = datetime.utcnow()
    
    result = await reviews_collection.insert_one(review_dict)
    review_dict["_id"] = result.inserted_id
    review_dict["id"] = str(result.inserted_id)
    
    return ReviewResponse(**review_dict)


async def get_reviews_by_product_service(product_id: str) -> list[ReviewResponse]:
    """
    Get all reviews for a specific product (internal service function).
    
    Args:
        product_id: Product ID
        
    Returns:
        List of reviews sorted by created_at (newest first)
    """
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Validate product_id format
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid product ID format: {product_id}"
        )
    
    reviews_collection = db.reviews
    cursor = reviews_collection.find({"product_id": product_id}).sort("created_at", -1)
    reviews = await cursor.to_list(length=1000)
    
    # Convert ObjectId to string and format response
    review_list = []
    for review in reviews:
        review["id"] = str(review["_id"])
        review_list.append(ReviewResponse(**review))
    
    return review_list


async def get_all_reviews_service(limit: int = 50) -> list[ReviewResponse]:
    """
    Get all reviews across all products (internal service function).
    
    Args:
        limit: Maximum number of reviews to return (default: 50)
        
    Returns:
        List of reviews sorted by created_at (newest first)
    """
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    reviews_collection = db.reviews
    cursor = reviews_collection.find({}).sort("created_at", -1).limit(limit)
    reviews = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string and format response
    review_list = []
    for review in reviews:
        review["id"] = str(review["_id"])
        review_list.append(ReviewResponse(**review))
    
    return review_list
