import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_discount, update_discount_usage

logger = logging.getLogger(__name__)

async def apply_discount(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Please enter your discount code:"
    )
    context.user_data['waiting_for_discount'] = True

async def apply_discount_callback(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    if context.user_data.get('waiting_for_discount'):
        discount_code = update.message.text.strip().upper()
        discount = get_discount(discount_code)
        
        if discount:
            # Check if discount is still valid
            if discount['max_uses'] != -1 and discount['used'] >= discount['max_uses']:
                await update.message.reply_text("❌ This discount code has reached its usage limit.")
            else:
                # Apply discount
                context.user_data['applied_discount'] = discount
                update_discount_usage(discount_code)
                
                await update.message.reply_text(
                    f"✅ Discount applied! {discount['percentage']}% off your order."
                )
        else:
            await update.message.reply_text("❌ Invalid discount code. Please try again.")
        
        context.user_data['waiting_for_discount'] = False
