"""
Notification service for sending Telegram messages.
"""
from telegram import Bot
import os
from dotenv import load_dotenv
from typing import Optional, List
import asyncio

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Global bot instance and admin chat IDs
bot: Optional[Bot] = None
admin_chat_ids: List[int] = []


async def initialize_bot():
    """
    Initialize Telegram bot instance and load admin chat IDs from env.
    """
    global bot, admin_chat_ids
    if TELEGRAM_BOT_TOKEN:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        # Parse ADMIN_CHAT_IDS from env
        admin_chat_ids_raw = os.getenv("ADMIN_CHAT_IDS", "")
        admin_chat_ids = [int(cid.strip()) for cid in admin_chat_ids_raw.split(",") if cid.strip().isdigit()]
        print(f"📋 Notification chat IDs loaded: {admin_chat_ids}")
        print("✅ Telegram notification bot initialized")
    else:
        print("⚠️ TELEGRAM_BOT_TOKEN not set, notifications disabled")


async def send_order_notification(order_data: dict):
    """
    Send order notification to all admin chat IDs via Telegram.
    
    Args:
        order_data: Dictionary containing order information
    """
    if not bot or not admin_chat_ids:
        print("⚠️ Telegram bot or admin chat IDs not configured, skipping notification")
        return
    
    # Format order details
    customer = order_data.get("customer", {})
    items = order_data.get("items", [])
    total = order_data.get("total", 0)
    order_id = order_data.get("id", "N/A")
    status = order_data.get("status", "pending")
    
    message = f"🛒 *New Order Received*\n\n"
    message += f"*Order ID:* `{order_id}`\n"
    message += f"*Status:* {status}\n\n"
    message += f"*Customer Information:*\n"
    message += f"👤 Name: {customer.get('name', 'N/A')}\n"
    message += f"📧 Email: {customer.get('email', 'N/A')}\n"
    message += f"📱 Phone: {customer.get('phone', 'N/A')}\n"
    message += f"📍 Address: {customer.get('address', 'N/A')}\n\n"
    message += f"*Items:*\n"
    
    for idx, item in enumerate(items, 1):
        message += f"{idx}. Product ID: `{item.get('product_id', 'N/A')}`\n"
        message += f"   Quantity: {item.get('quantity', 0)}\n"
        message += f"   Price: ${item.get('price', 0):.2f}\n"
    
    message += f"\n*Total Amount:* ${total:.2f}"
    
    # Send to all admin chat IDs
    for chat_id in admin_chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown"
            )
            print(f"✅ Order notification sent to admin chat ID: {chat_id}")
        except Exception as e:
            print(f"❌ Failed to send notification to chat ID {chat_id}: {e}")


async def send_message(chat_id: str, message: str, parse_mode: str = "Markdown"):
    """
    Send a generic message via Telegram bot.
    
    Args:
        chat_id: Target chat ID
        message: Message text
        parse_mode: Parse mode (Markdown, HTML, etc.)
    """
    if not bot:
        print("⚠️ Telegram bot not initialized")
        return
    
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=parse_mode
        )
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
