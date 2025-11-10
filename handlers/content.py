from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection

async def show_content(update: Update, context: ContextTypes.DEFAULT_TYPE, content_key: str) -> None:
    query = update.callback_query
    await query.answer()
    
    conn = get_db_connection()
    content = conn.execute('SELECT * FROM content WHERE key = ? AND active = 1', (content_key,)).fetchone()
    conn.close()
    
    if not content:
        await query.edit_message_text("❌ This page is currently unavailable.")
        return
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{content['title']}\n\n{content['content']}",
        reply_markup=reply_markup
    )

async def about_us(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_content(update, context, "about_us")

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_content(update, context, "contact")

async def website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_content(update, context, "website")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_content(update, context, "rules")

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_content(update, context, "faq")
