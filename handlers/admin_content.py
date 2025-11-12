from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection

async def admin_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("👋 Welcome Message", callback_data="admin_edit_welcome_message")],
        [InlineKeyboardButton("ℹ️ About Us", callback_data="admin_edit_about_us")],
        [InlineKeyboardButton("📞 Contact", callback_data="admin_edit_contact")],
        [InlineKeyboardButton("🌐 Website", callback_data="admin_edit_website")],
        [InlineKeyboardButton("📝 Rules", callback_data="admin_edit_rules")],
        [InlineKeyboardButton("🔍 FAQ", callback_data="admin_edit_faq")],
        [InlineKeyboardButton("🎉 Success Message", callback_data="admin_edit_success_message")],
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "📝 Content Management:\n\n"
        "Select page to edit content:",
        reply_markup=reply_markup
    )

async def admin_edit_content_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    content_key = query.data.replace("admin_edit_", "")
    
    conn = get_db_connection()
    content = conn.execute('SELECT * FROM content WHERE key = ?', (content_key,)).fetchone()
    conn.close()
    
    context.user_data['editing_content'] = content_key
    
    await query.edit_message_text(
        f"✏️ Edit '{content['title']}':\n\n"
        f"Current content:\n{content['content']}\n\n"
        f"Enter new content:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Content Management", callback_data="admin_content")
        ]])
    )

async def admin_edit_success_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    content_key = "success_message"
    
    conn = get_db_connection()
    content = conn.execute('SELECT * FROM content WHERE key = ?', (content_key,)).fetchone()
    conn.close()
    
    context.user_data['editing_content'] = content_key
    
    await query.edit_message_text(
        f"✏️ Edit '{content['title']}':\n\n"
        f"Current content:\n{content['content']}\n\n"
        f"Enter new content:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Content Management", callback_data="admin_content")
        ]])
    )

async def handle_content_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'editing_content' in context.user_data:
        content_key = context.user_data['editing_content']
        new_content = update.message.text
        
        conn = get_db_connection()
        conn.execute('UPDATE content SET content = ? WHERE key = ?', (new_content, content_key))
        conn.commit()
        conn.close()
        
        await update.message.reply_text("✅ Content updated!")
        del context.user_data['editing_content']
