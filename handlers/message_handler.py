from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import config

async def admin_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "Send the user ID and message in format:\n\n"
        "USER_ID Message text here\n\n"
        "Example:\n"
        "123456789 Hello, I am your shop bot!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]])
    )
    return 'WAITING_MESSAGE_DETAILS'

async def process_message_sending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    parts = text.split(' ', 1)
    
    if len(parts) < 2:
        await update.message.reply_text("Invalid format. Please try again.")
        return 'WAITING_MESSAGE_DETAILS'
    
    try:
        user_id = int(parts[0])
        message_text = parts[1]
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please try again.")
        return 'WAITING_MESSAGE_DETAILS'
    
    from main import application
    try:
        await application.bot.send_message(user_id, message_text)
        await update.message.reply_text(
            f"✅ Message sent to user {user_id}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]])
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to send message: {e}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]])
        )
    
    return -1
