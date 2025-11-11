import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_admin_stats, get_exchange_rate, update_exchange_rate

logger = logging.getLogger(__name__)

async def admin(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Products", callback_data='admin_products')],
        [InlineKeyboardButton("🎫 Discounts", callback_data='admin_discounts')],
        [InlineKeyboardButton("📝 Content", callback_data='admin_content')],
        [InlineKeyboardButton("💳 Payment Settings", callback_data='admin_payments')],
        [InlineKeyboardButton("💱 Exchange Rate", callback_data='admin_exchange_rate')],
        [InlineKeyboardButton("📊 Statistics", callback_data='admin_stats')],
        [InlineKeyboardButton("🔙 Back", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🏠 Admin Panel:", reply_markup=reply_markup)

async def admin_exchange_rate(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    current_rate = get_exchange_rate()
    
    keyboard = [
        [InlineKeyboardButton("Set Exchange Rate", callback_data='set_exchange_rate')],
        [InlineKeyboardButton("🔙 Back", callback_data='admin')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💱 Current Exchange Rate: 1 EUR = {current_rate} USD\n\n"
        "Set new exchange rate:",
        reply_markup=reply_markup
    )

async def set_exchange_rate(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Please enter the new exchange rate (e.g., 1.10 for 1 EUR = 1.10 USD):"
    )
    context.user_data['waiting_for_exchange_rate'] = True

async def handle_exchange_rate_input(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('waiting_for_exchange_rate'):
        try:
            rate_text = update.message.text.strip()
            rate = float(rate_text)
            if rate <= 0:
                await update.message.reply_text("❌ Please enter a positive number. Try again:")
                return
            
            update_exchange_rate(rate)
            context.user_data['waiting_for_exchange_rate'] = False
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Admin", callback_data='admin')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ Exchange rate updated to: 1 EUR = {rate} USD",
                reply_markup=reply_markup
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Please enter a valid exchange rate (e.g., 1.10):")
    else:
        # If not waiting for exchange rate, check if it's a general message
        await update.message.reply_text("Please use the menu to interact with the bot.")

async def admin_stats(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    stats = get_admin_stats()
    
    text = (
        "📊 Bot Statistics:\n\n"
        f"👥 Total Users: {stats.get('total_users', 0)}\n"
        f"📦 Total Orders: {stats.get('total_orders', 0)}\n"
        f"💰 Total Revenue: €{stats.get('total_revenue', 0):.2f}\n"
        f"🛍️ Active Products: {stats.get('active_products', 0)}\n"
        f"🎫 Active Discounts: {stats.get('active_discounts', 0)}\n"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='admin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def admin_back(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    await admin(update, context)
