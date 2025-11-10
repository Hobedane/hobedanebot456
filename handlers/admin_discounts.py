from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection
from utils.helpers import is_admin
from config import logger

async def admin_discounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("👤 Add Client-Specific", callback_data="add_client_discount")],
        [InlineKeyboardButton("🌍 Add General Discount", callback_data="add_general_discount")],
        [InlineKeyboardButton("📋 View All Codes", callback_data="view_all_discounts")],
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🎫 Discount Code Management:", reply_markup=reply_markup)

async def admin_add_client_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Enter client ID:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Discount Management", callback_data="admin_discounts")
        ]])
    )
    context.user_data['admin_mode'] = 'adding_client_discount_id'

async def admin_add_general_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Enter discount code:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Discount Management", callback_data="admin_discounts")
        ]])
    )
    context.user_data['admin_mode'] = 'adding_discount_code'
    context.user_data['new_discount'] = {'is_general': True}

async def view_all_discounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    
    conn = get_db_connection()
    discounts = conn.execute('''SELECT * FROM discount_codes ORDER BY is_general, created_at DESC''').fetchall()
    conn.close()
    
    if not discounts:
        await query.edit_message_text("❌ No discount codes added yet.")
        return
    
    message = "📋 All Discount Codes:\n\n"
    for discount in discounts:
        if discount['is_general']:
            message += f"🌍 General code: {discount['code']}\n"
        else:
            message += f"👤 Client code: {discount['code']}\n"
        message += f"📊 Discount: {discount['discount_percent']}%\n"
        message += f"📅 Valid until: {discount['expires']}\n"
        if discount['is_general']:
            uses = f"{discount['used_count']}/{'∞' if discount['max_uses'] == -1 else discount['max_uses']}"
            message += f"🔢 Uses: {uses}\n"
        status = "✅ ACTIVE" if discount['active'] else "❌ INACTIVE"
        message += f"🎯 Status: {status}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Discount Management", callback_data="admin_discounts")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
