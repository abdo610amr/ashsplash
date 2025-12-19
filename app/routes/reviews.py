"""
Review routes for handling review-related API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.models.review import ReviewCreate, ReviewResponse
from app.services.review_service import create_review_service, get_reviews_by_product_service, get_all_reviews_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate):
    """
    Create a new review for a product (public endpoint).
    
    Args:
        review: Review data
        
    Returns:
        Created review
    """
    try:
        return await create_review_service(review)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating review: {str(e)}"
        )


@router.get("", response_model=List[ReviewResponse], status_code=status.HTTP_200_OK)
async def get_all_reviews(limit: int = Query(50, ge=1, le=100)):
    """
    Get all reviews across all products (public endpoint).
    
    Args:
        limit: Maximum number of reviews to return (default: 50)
        
    Returns:
        List of reviews sorted by created_at (newest first)
    """
    try:
        return await get_all_reviews_service(limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching reviews: {str(e)}"
        )


@router.get("/{product_id}", response_model=List[ReviewResponse], status_code=status.HTTP_200_OK)
async def get_reviews_by_product(product_id: str):
    """
    Get all reviews for a specific product (public endpoint).
    
    Args:
        product_id: Product ID
        
    Returns:
        List of reviews sorted by created_at (newest first)
    """
    try:
        return await get_reviews_by_product_service(product_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching reviews: {str(e)}"
        )

