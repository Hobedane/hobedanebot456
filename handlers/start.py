from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection
from utils.helpers import is_admin

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    # Load welcome message from database
    conn = get_db_connection()
    welcome_content = conn.execute('SELECT * FROM content WHERE key = ?', ('welcome_message',)).fetchone()
    conn.close()
    
    welcome_text = welcome_content['content'] if welcome_content else "Hello! 👋 I am your store bot.\n\nChoose from the options below:"
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Browse Products", callback_data="view_products")],
        [InlineKeyboardButton("🛒 My Cart", callback_data="view_cart")],
        [InlineKeyboardButton("ℹ️ About Us", callback_data="about_us")],
        [InlineKeyboardButton("📞 Contact", callback_data="contact")],
        [InlineKeyboardButton("🌐 Website", callback_data="website")],
        [InlineKeyboardButton("📝 Rules", callback_data="rules")],
        [InlineKeyboardButton("🔍 FAQ", callback_data="faq")]
    ]
    
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("🛠️ Admin Panel", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)
