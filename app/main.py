"""
Main application entry point.
FastAPI backend (API only).
Telegram bots are run as separate Render Background Workers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import connect_to_mongo, close_mongo_connection
from app.routes import products, orders, reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting API...")

    # Connect to MongoDB
    await connect_to_mongo()

    print("✅ API started")

    yield

    print("🛑 Shutting down API...")

    await close_mongo_connection()

    print("✅ API shutdown complete")


app = FastAPI(
    title="E-Commerce Backend API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(reviews.router)


@app.get("/")
async def root():
    return {
        "message": "E-Commerce Backend API",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
