from telegram import Update
from telegram.ext import ContextTypes
from database import Session, Statistics
from utils.helpers import get_message, get_main_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Update statistics
    with Session() as session:
        stats = session.query(Statistics).first()
        if not stats:
            stats = Statistics()
            session.add(stats)
        stats.visits += 1
        session.commit()
    
    welcome_message = get_message('welcome')
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_keyboard()
    )

async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_message = get_message('rules')
    await update.callback_query.edit_message_text(
        rules_message,
        reply_markup=get_main_keyboard()
    )

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = "🤖 Crypto Shop Bot\n\nThis bot allows you to purchase digital products using cryptocurrency."
    await update.callback_query.edit_message_text(
        about_text,
        reply_markup=get_main_keyboard()
    )
