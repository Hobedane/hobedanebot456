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

async def handle_client_discount_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_client_discount_id':
        try:
            client_id = int(update.message.text)
            context.user_data['new_discount'] = {'client_id': client_id, 'is_general': False}
            context.user_data['admin_mode'] = 'adding_discount_code'
            await update.message.reply_text(
                f"✅ Client ID: {client_id}\n\n"
                f"Enter discount code:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Discount Management", callback_data="admin_discounts")
                ]])
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid ID! Enter a number:")

async def handle_discount_code_input_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_discount_code':
        code = update.message.text.upper()
        context.user_data['new_discount']['code'] = code
        context.user_data['admin_mode'] = 'adding_discount_percent'
        await update.message.reply_text(
            f"✅ Code: {code}\n\n"
            f"Enter discount percentage (example: 10):",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Discount Management", callback_data="admin_discounts")
            ]])
        )

async def handle_discount_percent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_discount_percent':
        try:
            percent = int(update.message.text)
            context.user_data['new_discount']['percent'] = percent
            context.user_data['admin_mode'] = 'adding_discount_expiry'
            await update.message.reply_text(
                f"✅ Discount: {percent}%\n\n"
                f"Enter expiry date (YYYY-MM-DD):",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Discount Management", callback_data="admin_discounts")
                ]])
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid percentage! Enter a number:")

async def handle_discount_expiry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_discount_expiry':
        expiry = update.message.text
        discount_data = context.user_data['new_discount']
        if discount_data['is_general']:
            context.user_data['admin_mode'] = 'adding_discount_max_uses'
            await update.message.reply_text(
                f"✅ Valid until: {expiry}\n\n"
                f"Enter maximum uses (-1 for unlimited):",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Discount Management", callback_data="admin_discounts")
                ]])
            )
        else:
            conn = get_db_connection()
            conn.execute('''INSERT INTO discount_codes (code, discount_percent, expires, is_general, client_id) 
                         VALUES (?, ?, ?, ?, ?)''', 
                         (discount_data['code'], discount_data['percent'], expiry, 0, discount_data['client_id']))
            conn.commit()
            conn.close()
            await update.message.reply_text(
                f"✅ Client-specific discount code added!\n"
                f"👤 Client ID: {discount_data['client_id']}\n"
                f"🎫 Code: {discount_data['code']}\n"
                f"📊 Discount: {discount_data['percent']}%\n"
                f"📅 Valid until: {expiry}"
            )
            context.user_data['admin_mode'] = None
            context.user_data['new_discount'] = None

async def handle_discount_max_uses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_discount_max_uses':
        try:
            max_uses = int(update.message.text)
            discount_data = context.user_data['new_discount']
            conn = get_db_connection()
            conn.execute('''INSERT INTO discount_codes (code, discount_percent, expires, is_general, max_uses) 
                         VALUES (?, ?, ?, ?, ?)''', 
                         (discount_data['code'], discount_data['percent'], discount_data.get('expiry'), 1, max_uses))
            conn.commit()
            conn.close()
            uses_text = "unlimited" if max_uses == -1 else f"{max_uses} uses"
            await update.message.reply_text(
                f"✅ General discount code added!\n"
                f"🎫 Code: {discount_data['code']}\n"
                f"📊 Discount: {discount_data['percent']}%\n"
                f"📅 Valid until: {discount_data.get('expiry', 'Not set')}\n"
                f"🔢 Max: {uses_text}"
            )
            context.user_data['admin_mode'] = None
            context.user_data['new_discount'] = None
        except ValueError:
            await update.message.reply_text("❌ Invalid number! Enter a number:")
