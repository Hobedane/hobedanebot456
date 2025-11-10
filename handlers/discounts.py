from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Session, DiscountCode

async def admin_discounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Create Discount Code", callback_data="create_discount")],
        [InlineKeyboardButton("📋 List Discount Codes", callback_data="list_discounts")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]
    ]
    
    await update.callback_query.edit_message_text(
        "🎫 Discount Code Management:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def create_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "Send the discount code details in format:\n\n"
        "CODE PERCENT [USER_ID or USERNAME]\n\n"
        "Examples:\n"
        "SUMMER10 10\n"
        "VIP20 20 123456789\n"
        "SPECIAL15 15 @username",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_discounts")]])
    )
    return 'WAITING_DISCOUNT_DETAILS'

async def process_discount_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split()
    
    if len(parts) < 2:
        await update.message.reply_text("Invalid format. Please try again.")
        return 'WAITING_DISCOUNT_DETAILS'
    
    code = parts[0].upper()
    try:
        percent = float(parts[1])
    except ValueError:
        await update.message.reply_text("Invalid percentage. Please try again.")
        return 'WAITING_DISCOUNT_DETAILS'
    
    user_id = None
    username = None
    
    if len(parts) > 2:
        if parts[2].startswith('@'):
            username = parts[2][1:]  # Remove @
        else:
            try:
                user_id = int(parts[2])
            except ValueError:
                await update.message.reply_text("Invalid user ID. Please try again.")
                return 'WAITING_DISCOUNT_DETAILS'
    
    with Session() as session:
        discount = DiscountCode(
            code=code,
            discount_percent=percent,
            user_id=user_id,
            username=username
        )
        session.add(discount)
        session.commit()
    
    await update.message.reply_text(
        f"✅ Discount code created!\nCode: {code}\nDiscount: {percent}%",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]])
    )
    return -1
