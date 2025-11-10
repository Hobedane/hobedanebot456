from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection
from utils.helpers import is_admin
from config import logger

async def admin_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    
    conn = get_db_connection()
    payments = conn.execute('SELECT * FROM payment_settings').fetchall()
    conn.close()
    
    message = "💳 Payment Settings:\n\n"
    keyboard = []
    
    for payment in payments:
        name = {
            'btc': '₿ Bitcoin',
            'eth': 'Ξ Ethereum',
            'sol': '◎ Solana', 
            'ltc': '💎 Litecoin',
            'usdt': '💵 USDT'
        }.get(payment['crypto_type'], payment['crypto_type'].upper())
        message += f"{name}:\n{payment['address']}\n\n"
        keyboard.append([
            InlineKeyboardButton(f"✏️ Edit {name}", callback_data=f"edit_payment_{payment['crypto_type']}"),
            InlineKeyboardButton(f"🗑️ Remove {name}", callback_data=f"remove_payment_{payment['crypto_type']}")
        ])
    
    keyboard.append([InlineKeyboardButton("➕ Add New Crypto", callback_data="add_new_crypto")])
    keyboard.append([InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")])
    keyboard.append([InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")

async def edit_payment_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    crypto_type = query.data.replace("edit_payment_", "")
    
    conn = get_db_connection()
    payment = conn.execute('SELECT * FROM payment_settings WHERE crypto_type = ?', (crypto_type,)).fetchone()
    conn.close()
    
    context.user_data['editing_payment'] = crypto_type
    name = {
        'btc': 'Bitcoin',
        'eth': 'Ethereum',
        'sol': 'Solana',
        'ltc': 'Litecoin', 
        'usdt': 'USDT'
    }.get(crypto_type, crypto_type.upper())
    
    await query.edit_message_text(
        f"✏️ Edit {name} address:\n\n"
        f"Current address:\n{payment['address']}\n\n"
        f"Enter new address:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Payment Settings", callback_data="admin_payments")
        ]])
    )

async def remove_payment_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    crypto_type = query.data.replace("remove_payment_", "")
    
    name = {
        'btc': 'Bitcoin',
        'eth': 'Ethereum',
        'sol': 'Solana',
        'ltc': 'Litecoin',
        'usdt': 'USDT'
    }.get(crypto_type, crypto_type.upper())
    
    keyboard = [
        [
            InlineKeyboardButton("✅ YES, remove", callback_data=f"confirm_remove_{crypto_type}"),
            InlineKeyboardButton("❌ NO, cancel", callback_data="admin_payments")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔍 CONFIRMATION\n\n"
        f"Are you sure you want to remove {name} as payment method?\n\n"
        f"⚠️ This action cannot be undone!",
        reply_markup=reply_markup
    )

async def add_new_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "➕ Add new cryptocurrency:\n\n"
        "Enter currency code (btc, eth, sol, ltc, usdt):",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Payment Settings", callback_data="admin_payments")
        ]])
    )
    context.user_data['admin_mode'] = 'adding_crypto_type'
