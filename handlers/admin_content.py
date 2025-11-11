import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import get_content, update_content

logger = logging.getLogger(__name__)

# States for content conversation
ADMIN_CONTENT, ADMIN_CONTENT_SUCCESS, ADMIN_CONTENT_WELCOME = range(3)

async def admin_content(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    content = get_content()
    
    keyboard = [
        [InlineKeyboardButton("Success Message", callback_data='content_success')],
        [InlineKeyboardButton("Welcome Message", callback_data='content_welcome')],
        [InlineKeyboardButton("Back", callback_data='admin_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Content Management:\n\n"
        f"Current Welcome Message: {content.get('welcome_message', 'Not set')[:50]}...\n"
        f"Current Success Message: {content.get('success_message', 'Not set')[:50]}...",
        reply_markup=reply_markup
    )

async def content_success(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    current_content = get_content()
    current_message = current_content.get('success_message', 'Not set')
    
    await query.edit_message_text(
        f"Current Success Message:\n{current_message}\n\n"
        "Please enter the new success message:"
    )
    return ADMIN_CONTENT_SUCCESS

async def content_success_input(update: Update, context: CallbackContext) -> int:
    success_message = update.message.text.strip()
    
    if not success_message:
        await update.message.reply_text("Message cannot be empty. Please enter a valid message:")
        return ADMIN_CONTENT_SUCCESS
    
    update_content('success_message', success_message)
    
    keyboard = [[InlineKeyboardButton("Back to Content", callback_data='admin_content')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("✅ Success message updated!", reply_markup=reply_markup)
    return ConversationHandler.END

async def content_welcome(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    current_content = get_content()
    current_message = current_content.get('welcome_message', 'Not set')
    
    await query.edit_message_text(
        f"Current Welcome Message:\n{current_message}\n\n"
        "Please enter the new welcome message:"
    )
    return ADMIN_CONTENT_WELCOME

async def content_welcome_input(update: Update, context: CallbackContext) -> int:
    welcome_message = update.message.text.strip()
    
    if not welcome_message:
        await update.message.reply_text("Message cannot be empty. Please enter a valid message:")
        return ADMIN_CONTENT_WELCOME
    
    update_content('welcome_message', welcome_message)
    
    keyboard = [[InlineKeyboardButton("Back to Content", callback_data='admin_content')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("✅ Welcome message updated!", reply_markup=reply_markup)
    return ConversationHandler.END

async def cancel_content(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Content update canceled.')
    return ConversationHandler.END
