from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection, get_exchange_rate, update_exchange_rate

async def admin_exchange_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    current_rate = get_exchange_rate()
    
    message = (
        f"💰 Exchange Rate Management\n\n"
        f"Current rate: 1 EUR = {current_rate} USD\n\n"
        f"Enter new exchange rate (e.g., 1.16 for 1 EUR = 1.16 USD):"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)
    context.user_data['admin_mode'] = 'editing_exchange_rate'

async def handle_exchange_rate_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'editing_exchange_rate':
        try:
            new_rate = float(update.message.text)
            if new_rate <= 0:
                await update.message.reply_text("❌ Exchange rate must be positive! Try again:")
                return
            
            update_exchange_rate(new_rate)
            
            await update.message.reply_text(
                f"✅ Exchange rate updated!\n\n"
                f"New rate: 1 EUR = {new_rate} USD\n\n"
                f"All prices will now show both EUR and USD amounts.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")
                ]])
            )
            
            context.user_data['admin_mode'] = None
            
        except ValueError:
            await update.message.reply_text("❌ Invalid exchange rate! Enter a number (e.g., 1.16):")
