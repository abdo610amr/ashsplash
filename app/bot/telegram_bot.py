"""
Telegram Admin Bot – FastAPI Compatible
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import os
from dotenv import load_dotenv

from app.database import get_database
from app.models.product import ProductCreate
from app.services.product_service import (
    create_product_service,
    delete_product_service,
    set_product_availability_service,
    set_product_price_service
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot_application: Application | None = None
admin_usernames: list[str] = []

# user_id -> product_id
pending_price_update: dict[int, str] = {}
pending_description_update: dict[int, str] = {}

# ================= ADMIN CHECK ================= #

def is_admin(update: Update) -> bool:
    user = update.effective_user
    if not user or not user.username:
        return False
    return user.username.lower() in admin_usernames


# ================= MESSAGES ================= #

START_MESSAGE = (
    "👋 *Welcome to E-Commerce Admin Bot*\n\n"
    "You can manage your store directly from Telegram.\n\n"
    "📦 *Products*\n"
    "• /products – List products\n"
    "• /addproduct name|price|true|men\n"
    "• /deleteproduct <id>\n\n"
    "ℹ️ Use /help for details"
)

HELP_MESSAGE = (
    "🆘 *Admin Bot Help*\n\n"
    "➕ Add Product:\n"
    "`/addproduct Name|Price|true|men`\n\n"
    "📦 List Products:\n"
    "`/products`\n\n"
    "🗑 Delete Product:\n"
    "`/deleteproduct <id>`\n\n"
    "💰 Change Price:\n"
    "Press *Change Price* → send number فقط\n\n"
    "⚠️ gender must be `men` or `women`"
)

# ================= COMMANDS ================= #

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("❌ Unauthorized")
        return
    await update.message.reply_text(START_MESSAGE, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")

async def products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return

    db = get_database()
    products = await db.products.find({}).to_list(100)

    if not products:
        await update.message.reply_text("📦 No products found")
        return

    for p in products:
        keyboard = [
            [
                InlineKeyboardButton("🟥 Sold Out", callback_data=f"soldout:{p['_id']}"),
                InlineKeyboardButton("🟩 Available", callback_data=f"available:{p['_id']}")
            ],
            [
                InlineKeyboardButton("💰 Change Price", callback_data=f"price:{p['_id']}"),
                InlineKeyboardButton("✏️ Description", callback_data=f"desc:{p['_id']}")
            ],
            [    
                InlineKeyboardButton("🗑 Delete", callback_data=f"delete:{p['_id']}")
            ]
        ]

        await update.message.reply_text(
            f"🛒 *{p['name']}*\n"
            f"🆔 `{p['_id']}`\n"
            f"💵 {p['price']} EGP\n"
            f"👕 {p.get('gender', 'N/A')}\n"
            f"📦 {'Available ✅' if p.get('available') else 'Sold Out ❌'}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def addproduct_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return

    try:
        name, price, available, gender = " ".join(context.args).split("|")

        if gender not in ["men", "women"]:
            await update.message.reply_text("❌ gender must be men or women")
            return

        product = ProductCreate(
            name=name.strip(),
            price=float(price),
            available=available.lower() in ["true", "1", "yes"],
            gender=gender
        )

        created = await create_product_service(product)

        await update.message.reply_text(
            f"✅ *Product Added*\n\n"
            f"{created.name}\n"
            f"{created.price} EGP\n"
            f"{created.gender}",
            parse_mode="Markdown"
        )

    except Exception:
        await update.message.reply_text(
            "❌ Wrong format\n`/addproduct Name|Price|true|men`",
            parse_mode="Markdown"
        )


async def deleteproduct_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return

    try:
        await delete_product_service(context.args[0])
        await update.message.reply_text("🗑 Product deleted")
    except:
        await update.message.reply_text("❌ Invalid product ID")


# ================= CALLBACKS ================= #

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(update):
        await query.edit_message_text("❌ Unauthorized")
        return

    action, product_id = query.data.split(":")

    try:
        if action == "soldout":
            await set_product_availability_service(product_id, False)
            await query.edit_message_text("🟥 Marked as SOLD OUT")

        elif action == "available":
            await set_product_availability_service(product_id, True)
            await query.edit_message_text("🟩 Marked as AVAILABLE")

        elif action == "price":
            pending_price_update[query.from_user.id] = product_id
            await query.edit_message_text(
                "💰 Send new price\nExample:\n`300`",
                parse_mode="Markdown"
            )
        elif action == "delete":
            await delete_product_service(product_id)
            await query.edit_message_text("🗑 Product deleted successfully")
        elif action == "desc":
            pending_description_update[query.from_user.id] = product_id
            await query.edit_message_text(
                "✏️ *Send product description*\n\n"
                "You can write multiple lines.\n"
                "Example:\n"
                "`Fresh floral scent with long lasting notes`",
                parse_mode="Markdown"
            )
    except Exception as e:
        await query.edit_message_text(f"❌ {e}")


async def price_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pending_price_update:
        return

    try:
        price = float(update.message.text)
        product_id = pending_price_update.pop(user_id)
        await set_product_price_service(product_id, price)
        await update.message.reply_text(f"✅ Price updated → {price} EGP")
    except:
        await update.message.reply_text("❌ Send valid number")


# ================= INIT / START / STOP ================= #

async def initialize_telegram_bot():
    global bot_application, admin_usernames

    admin_usernames = [
        u.strip().lower().lstrip("@")
        for u in os.getenv("ADMIN_USERNAMES", "").split(",")
        if u.strip()
    ]

    bot_application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    bot_application.add_handler(CommandHandler("start", start_command))
    bot_application.add_handler(CommandHandler("help", help_command))
    bot_application.add_handler(CommandHandler("products", products_command))
    bot_application.add_handler(CommandHandler("addproduct", addproduct_command))
    bot_application.add_handler(CommandHandler("deleteproduct", deleteproduct_command))
    bot_application.add_handler(CallbackQueryHandler(callback_handler))
    bot_application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, price_message_handler)
    )

    print("✅ Telegram admin bot initialized")
    return bot_application


async def start_bot_polling():
    await bot_application.initialize()
    await bot_application.start()
    await bot_application.updater.start_polling()
    print("🤖 Bot polling started")


async def stop_bot_polling():
    await bot_application.updater.stop()
    await bot_application.stop()
    await bot_application.shutdown()
    print("🛑 Bot stopped")
# ================= WORKER ENTRY POINT ================= #

import asyncio

async def run_bot():
    await initialize_telegram_bot()
    await start_bot_polling()

if __name__ == "__main__":
    asyncio.run(run_bot())
