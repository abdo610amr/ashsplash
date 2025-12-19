from fastapi import HTTPException, status
from app.models.product import ProductCreate, ProductResponse
from app.database import get_database
from bson import ObjectId
from datetime import datetime


async def create_product_service(product: ProductCreate) -> ProductResponse:
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )

    product_dict = product.dict()
    product_dict["created_at"] = datetime.utcnow()
    product_dict["updated_at"] = datetime.utcnow()

    result = await db.products.insert_one(product_dict)

    product_dict["_id"] = result.inserted_id
    product_dict["id"] = str(result.inserted_id)

    return ProductResponse(**product_dict)


async def delete_product_service(product_id: str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")

    db = get_database()
    result = await db.products.delete_one({"_id": ObjectId(product_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")


async def set_product_availability_service(product_id: str, available: bool):
    if not ObjectId.is_valid(product_id):
        raise ValueError("Invalid product ID")

    db = get_database()
    result = await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"available": available}}
    )

    if result.matched_count == 0:
        raise ValueError("Product not found")


async def set_product_price_service(product_id: str, price: float):
    if not ObjectId.is_valid(product_id):
        raise ValueError("Invalid product ID")

    db = get_database()
    result = await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"price": price}}
    )

    if result.matched_count == 0:
        raise ValueError("Product not found")
async def set_product_description_service(product_id: str, description: str):
    if not ObjectId.is_valid(product_id):
        raise ValueError("Invalid product ID")

    db = get_database()
    result = await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"description": description}}
    )

    if result.matched_count == 0:
        raise ValueError("Product not found")
