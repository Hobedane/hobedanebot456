from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection, update_exchange_rate, get_exchange_rate
from utils.helpers import is_admin
from config import logger

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        if update.message:
            await update.message.reply_text("❌ No access!")
        else:
            await update.callback_query.answer("❌ No access!")
        return

    query = update.callback_query
    if query:
        await query.answer()

    keyboard = [
        [InlineKeyboardButton("📦 Product Management", callback_data="admin_products")],
        [InlineKeyboardButton("📝 Content Management", callback_data="admin_content")],
        [InlineKeyboardButton("💳 Payment Settings", callback_data="admin_payments")],
        [InlineKeyboardButton("🎫 Discount Codes", callback_data="admin_discounts")],
        [InlineKeyboardButton("💰 Exchange Rate", callback_data="admin_exchange_rate")],  # NEW
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text("🛠️ Admin Panel:", reply_markup=reply_markup)
    else:
        await query.edit_message_text("🛠️ Admin Panel:", reply_markup=reply_markup)

# NEW: Exchange rate management
async def admin_exchange_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    current_rate = get_exchange_rate()
    
    message = (
        f"💰 Exchange Rate Management\n\n"
        f"Current rate: 1 EUR = {current_rate} USD\n\n"
        f"Enter new exchange rate (example: 1.16):"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)
    context.user_data['admin_mode'] = 'updating_exchange_rate'

async def handle_exchange_rate_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'updating_exchange_rate':
        try:
            new_rate = float(update.message.text)
            if new_rate <= 0:
                await update.message.reply_text("❌ Rate must be positive! Enter new rate:")
                return
            
            update_exchange_rate(new_rate)
            await update.message.reply_text(
                f"✅ Exchange rate updated!\n\n"
                f"New rate: 1 EUR = {new_rate} USD\n\n"
                f"Prices will now display in both EUR and USD.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")
                ]])
            )
            context.user_data['admin_mode'] = None
            
        except ValueError:
            await update.message.reply_text("❌ Invalid rate! Enter a number (example: 1.16):")

# Product management functions would continue here...
# (admin_products, admin_edit_product, etc. - similar structure as original)
