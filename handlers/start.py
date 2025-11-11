import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_content, add_user
from config import ADMINS

logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    add_user(user.id, user.username, user.first_name, user.last_name)
    
    content = get_content()
    welcome_message = content.get('welcome_message', 'Welcome to our store! 🛍️')
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Products", callback_data='products')],
        [InlineKeyboardButton("🛒 Cart", callback_data='cart')],
        [InlineKeyboardButton("🎫 Discounts", callback_data='apply_discount')],
        [InlineKeyboardButton("ℹ️ About", callback_data='about')]
    ]
    
    # Add admin button for admins
    if user.id in ADMINS:
        keyboard.append([InlineKeyboardButton("👑 Admin", callback_data='admin')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_message, reply_markup=reply_markup)

async def about(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    text = (
        "🤖 About Our Store\n\n"
        "Welcome to our Telegram bot store! "
        "We offer various products with secure payment methods.\n\n"
        "Features:\n"
        "• 🛍️ Browse products\n"
        "• 🛒 Easy shopping cart\n"
        "• 🎫 Discount codes\n"
        "• 💳 Multiple payment options\n"
        "• 🔒 Secure transactions\n\n"
        "For support, please contact us."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)
