from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.product import ProductCreate, ProductResponse
from app.auth import verify_admin_key
from app.services.product_service import create_product_service, delete_product_service
from app.database import get_database
from bson import ObjectId

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[ProductResponse])
async def get_products():
    db = get_database()
    products = await db.products.find({}).to_list(1000)

    result = []
    for p in products:
        p["id"] = str(p["_id"])

        # ✅ FIX: handle old products without gender
        if "gender" not in p:
            p["gender"] = "women"

        result.append(ProductResponse(**p))

    return result


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    _: bool = Depends(verify_admin_key)
):
    return await create_product_service(product)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    _: bool = Depends(verify_admin_key)
):
    await delete_product_service(product_id)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")

    db = get_database()
    product = await db.products.find_one({"_id": ObjectId(product_id)})

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product["id"] = str(product["_id"])

    # ✅ FIX هنا كمان
    if "gender" not in product:
        product["gender"] = "women"

    return ProductResponse(**product)
