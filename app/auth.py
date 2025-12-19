"""
Admin authentication dependency for FastAPI.
"""
from fastapi import Header, HTTPException, status
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


async def verify_admin_key(x_admin_key: Optional[str] = Header(None, alias="X-ADMIN-KEY")):
    """
    Dependency to verify admin API key from X-ADMIN-KEY header.
    
    Args:
        x_admin_key: API key from X-ADMIN-KEY header
        
    Raises:
        HTTPException: 401 if key is missing or invalid
    """
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin API key not configured"
        )
    
    if not x_admin_key or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key"
        )
    
    return True

