from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Session, CustomMessage
from utils.helpers import get_message

async def admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session() as session:
        messages = session.query(CustomMessage).all()
        message_dict = {msg.key: msg.value for msg in messages}
    
    keyboard = []
    available_messages = [
        ('welcome', 'Welcome Message'),
        ('success_payment', 'Success Payment Message'),
        ('rules', 'Rules Text'),
        ('added_to_cart', 'Added to Cart Message'),
        ('payment_instructions', 'Payment Instructions')
    ]
    
    for key, description in available_messages:
        current_value = message_dict.get(key, get_message(key))
        preview = current_value[:50] + "..." if len(current_value) > 50 else current_value
        keyboard.append([InlineKeyboardButton(
            f"✏️ {description}",
            callback_data=f"edit_message_{key}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")])
    
    text = "⚙️ Customize Messages\n\nClick on a message to edit it."
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_key = update.callback_query.data.split('_')[-1]
    current_value = get_message(message_key)
    
    context.user_data['editing_message'] = message_key
    
    await update.callback_query.edit_message_text(
        f"Editing: {message_key}\n\nCurrent value:\n{current_value}\n\n"
        f"Please send the new value:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_messages")]])
    )
    return 'WAITING_MESSAGE_UPDATE'

async def process_message_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_value = update.message.text
    message_key = context.user_data.get('editing_message')
    
    if not message_key:
        await update.message.reply_text("Error: No message key found.")
        return -1
    
    with Session() as session:
        existing = session.query(CustomMessage).filter_by(key=message_key).first()
        if existing:
            existing.value = new_value
        else:
            new_message = CustomMessage(key=message_key, value=new_value)
            session.add(new_message)
        session.commit()
    
    if 'editing_message' in context.user_data:
        del context.user_data['editing_message']
    
    await update.message.reply_text(
        f"✅ Message updated successfully!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]])
    )
    return -1
