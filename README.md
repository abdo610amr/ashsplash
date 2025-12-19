# FastAPI + MongoDB Atlas + Telegram Bot Backend

A production-ready backend application built with FastAPI, MongoDB Atlas, and Telegram Bot integration.

## Features

- RESTful API with FastAPI
- MongoDB Atlas integration using Motor (async)
- Telegram Bot for admin management
- Product, Order, and Review management
- Real-time notifications via Telegram

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

3. Configure your `.env` file:
   - Add your MongoDB Atlas connection string
   - Add your Telegram Bot token
   - Add your admin chat ID

4. Run the application:
```bash
python -m app.main
```

## API Endpoints

### Products
- `GET /products` - Get all products (public)

### Orders
- `POST /orders` - Create a new order (public)

## Telegram Bot Commands

- `/products` - List all products
- `/addproduct` - Add a new product
- `/deleteproduct` - Delete a product
- `/updatestatus` - Update order status

## Project Structure

```
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   ├── product.py
│   │   ├── order.py
│   │   └── review.py
│   ├── routes/
│   │   ├── products.py
│   │   └── orders.py
│   ├── services/
│   │   └── notify.py
│   └── bot/
│       └── telegram_bot.py
├── .env.example
├── requirements.txt
└── README.md
```

