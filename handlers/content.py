import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_content

logger = logging.getLogger(__name__)

async def welcome_message(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    content = get_content()
    welcome_msg = content.get('welcome_message', 'Welcome to our store! 🛍️')
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📝 Welcome Message:\n\n{welcome_msg}",
        reply_markup=reply_markup
    )

async def success_message(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    content = get_content()
    success_msg = content.get('success_message', 'Thank you for your purchase! ✅')
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📝 Success Message:\n\n{success_msg}",
        reply_markup=reply_markup
    )
