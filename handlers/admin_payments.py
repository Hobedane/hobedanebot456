import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_payment_methods, toggle_payment_method

logger = logging.getLogger(__name__)

async def admin_payments(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    payment_methods_list = get_payment_methods()
    
    keyboard = []
    for method in payment_methods_list:
        status = "✅ Enabled" if method['enabled'] else "❌ Disabled"
        keyboard.append([
            InlineKeyboardButton(
                f"{method['method'].title()} - {status}", 
                callback_data=f"toggle_payment_{method['method']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='admin')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("💳 Payment Methods Settings:", reply_markup=reply_markup)

async def toggle_payment(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    method = query.data.replace('toggle_payment_', '')
    current_methods = get_payment_methods()
    
    # Find current status
    current_status = None
    for pm in current_methods:
        if pm['method'] == method:
            current_status = pm['enabled']
            break
    
    if current_status is not None:
        # Toggle the status
        new_status = not current_status
        toggle_payment_method(method, new_status)
        
        status_text = "enabled" if new_status else "disabled"
        await query.edit_message_text(f"✅ {method.title()} payment method has been {status_text}!")
    
    # Return to payment settings
    await admin_payments(update, context)
