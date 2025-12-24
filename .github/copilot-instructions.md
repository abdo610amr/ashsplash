# AI Coding Guidelines for E-Commerce Backend

## Architecture Overview
This is a FastAPI-based e-commerce backend with MongoDB Atlas and Telegram bot integration. The app uses async operations throughout for scalability.

**Key Components:**
- **API Layer**: FastAPI with async endpoints in `app/routes/`
- **Business Logic**: Service functions in `app/services/` handle validation and DB operations
- **Data Models**: Pydantic schemas in `app/models/` with Base/Create/DB patterns
- **Database**: Motor (async MongoDB driver) with connection management via lifespan
- **Admin Interface**: Separate Telegram bot in `app/bot/` for product/order management
- **Authentication**: X-ADMIN-KEY header for protected endpoints

## Core Patterns

### Model Definitions
Use Pydantic with inheritance pattern:
```python
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    # shared fields

class ProductCreate(ProductBase):
    pass  # for input validation

class Product(ProductBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # DB fields
```

**Custom ObjectId**: Always use `PyObjectId` for MongoDB `_id` fields, defined in `app/models/product.py`.

### Route Structure
Routes are thin wrappers that delegate to services:
```python
@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    _: bool = Depends(verify_admin_key)  # auth dependency
):
    return await create_product_service(product)
```

### Service Layer
Services handle business logic, validation, and DB operations:
- Validate ObjectId format: `if not ObjectId.is_valid(product_id): raise HTTPException(...)`
- Check DB availability: `if db is None: raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE)`
- Use detailed error messages and appropriate HTTP status codes
- Update `updated_at` timestamps on modifications

### Database Operations
- Use `get_database()` from `app.database` for DB access
- Async operations: `await db.collection.find_one(...)`
- Convert ObjectId to string for responses: `product_dict["id"] = str(result.inserted_id)`

### Authentication
Admin endpoints use `Depends(verify_admin_key)` which checks `X-ADMIN-KEY` header against `ADMIN_API_KEY` env var.

### Telegram Integration
- Bot runs separately from API (see Procfile)
- Uses `python-telegram-bot` library
- Admin usernames configured in code (not env)
- Notifications sent to `ADMIN_CHAT_IDS` (comma-separated env var)

## Development Workflow

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Add MONGO_URI, DB_NAME, ADMIN_API_KEY, TELEGRAM_BOT_TOKEN, ADMIN_CHAT_IDS

# Run API
python -m app.main

# Bot runs as separate process (see Procfile for deployment)
```

### Environment Variables
All configuration via `.env`:
- `MONGO_URI`: MongoDB Atlas connection string
- `DB_NAME`: Database name (default: "ecommerce")
- `ADMIN_API_KEY`: API key for admin endpoints
- `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather
- `ADMIN_CHAT_IDS`: Comma-separated Telegram chat IDs for notifications

### Deployment
- Uses Procfile for Heroku/Render deployment
- API and bot run as separate processes
- Lifespan manages DB connections

## Key Files to Reference
- `app/main.py`: App setup and route inclusion
- `app/database.py`: DB connection management
- `app/models/product.py`: Model patterns and PyObjectId
- `app/services/product_service.py`: Service layer example
- `app/auth.py`: Authentication dependency
- `app/bot/telegram_bot.py`: Bot implementation patterns</content>
<parameter name="filePath">c:\abdo\ash project\backend\.github\copilot-instructions.md