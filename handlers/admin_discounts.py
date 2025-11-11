import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import get_discounts, add_discount, update_discount, delete_discount

logger = logging.getLogger(__name__)

# States for discount conversation
DISCOUNT_CODE, DISCOUNT_PERCENTAGE, DISCOUNT_MAX_USES, DISCOUNT_CONFIRM = range(4)

async def admin_discounts(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Add Discount", callback_data='add_discount')],
        [InlineKeyboardButton("View All Discounts", callback_data='view_discounts')],
        [InlineKeyboardButton("Back", callback_data='admin_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Discount Management:", reply_markup=reply_markup)

async def add_discount_start(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Enter discount code:")
    return DISCOUNT_CODE

async def add_discount_code(update: Update, context: CallbackContext) -> int:
    code = update.message.text.strip()
    if not code:
        await update.message.reply_text("Please enter a valid discount code:")
        return DISCOUNT_CODE
    
    context.user_data['discount_code'] = code
    await update.message.reply_text("Enter discount percentage (e.g., 10 for 10%):")
    return DISCOUNT_PERCENTAGE

async def add_discount_percentage(update: Update, context: CallbackContext) -> int:
    try:
        percentage = float(update.message.text.strip())
        if percentage <= 0 or percentage > 100:
            await update.message.reply_text("Please enter a valid percentage between 1 and 100:")
            return DISCOUNT_PERCENTAGE
    except ValueError:
        await update.message.reply_text("Invalid percentage. Please enter a number:")
        return DISCOUNT_PERCENTAGE
    
    context.user_data['discount_percentage'] = percentage
    await update.message.reply_text("Enter maximum uses (or -1 for unlimited):")
    return DISCOUNT_MAX_USES

async def add_discount_max_uses(update: Update, context: CallbackContext) -> int:
    try:
        max_uses = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Invalid number. Please enter a number for maximum uses:")
        return DISCOUNT_MAX_USES
    
    context.user_data['discount_max_uses'] = max_uses
    
    # Confirmation
    code = context.user_data['discount_code']
    percentage = context.user_data['discount_percentage']
    max_uses = context.user_data['discount_max_uses']
    
    keyboard = [
        [InlineKeyboardButton("Confirm", callback_data='confirm_discount')],
        [InlineKeyboardButton("Cancel", callback_data='cancel_discount')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Discount Details:\n"
        f"Code: {code}\n"
        f"Percentage: {percentage}%\n"
        f"Max Uses: {max_uses if max_uses != -1 else 'Unlimited'}\n\n"
        f"Confirm adding this discount?",
        reply_markup=reply_markup
    )
    return DISCOUNT_CONFIRM

async def add_discount_confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_discount':
        code = context.user_data['discount_code']
        percentage = context.user_data['discount_percentage']
        max_uses = context.user_data['discount_max_uses']
        
        add_discount(code, percentage, max_uses)
        await query.edit_message_text("✅ Discount added successfully!")
    else:
        await query.edit_message_text("❌ Discount addition canceled.")
    
    return ConversationHandler.END

async def view_discounts(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    discounts = get_discounts()
    if not discounts:
        await query.edit_message_text("No discounts found.")
        return
    
    text = "📋 All Discount Codes:\n\n"
    for discount in discounts:
        used = discount.get('used', 0)
        max_uses = discount.get('max_uses', 0)
        status = "🟢 Active" if discount.get('active', True) else "🔴 Inactive"
        
        text += (
            f"Code: {discount['code']}\n"
            f"Percentage: {discount['percentage']}%\n"
            f"Used: {used}/{max_uses if max_uses != -1 else 'Unlimited'}\n"
            f"Status: {status}\n"
            f"────────────────────\n"
        )
    
    keyboard = [[InlineKeyboardButton("Back", callback_data='admin_discounts')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def cancel_discount(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Discount addition canceled.')
    return ConversationHandler.END
