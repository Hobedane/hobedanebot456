from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.helpers import is_admin

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ No access!") if update.message else await update.callback_query.answer("❌ No access!")
        return
    
    query = update.callback_query
    if query:
        await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📦 Product Management", callback_data="admin_products")],
        [InlineKeyboardButton("📝 Content Management", callback_data="admin_content")],
        [InlineKeyboardButton("💳 Payment Settings", callback_data="admin_payments")],
        [InlineKeyboardButton("🎫 Discount Codes", callback_data="admin_discounts")],
        [InlineKeyboardButton("💰 Exchange Rate", callback_data="admin_exchange_rate")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text("🛠️ Admin Panel:", reply_markup=reply_markup)
    else:
        await query.edit_message_text("🛠️ Admin Panel:", reply_markup=reply_markup)
