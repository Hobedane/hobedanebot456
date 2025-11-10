from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import config
from database import Session, CustomMessage

def get_message(key, default=None):
    with Session() as session:
        custom_msg = session.query(CustomMessage).filter_by(key=key).first()
        if custom_msg:
            return custom_msg.value
        return config.DEFAULT_MESSAGES.get(key, default)

def format_price_eur(price):
    return f"€{price:.2f}"

def format_price_usd(price_eur):
    usd_price = price_eur * config.EXCHANGE_RATE
    return f"${usd_price:.2f}"

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛍️ Products", callback_data="products")],
        [InlineKeyboardButton("🛒 Cart", callback_data="cart")],
        [InlineKeyboardButton("📋 Rules", callback_data="rules")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("📦 Manage Products", callback_data="admin_products")],
        [InlineKeyboardButton("💰 Crypto Addresses", callback_data="admin_crypto")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ Customize Messages", callback_data="admin_messages")],
        [InlineKeyboardButton("🎫 Discount Codes", callback_data="admin_discounts")],
        [InlineKeyboardButton("💳 Pending Payments", callback_data="admin_payments")],
        [InlineKeyboardButton("💬 Send Message", callback_data="admin_send_msg")]
    ]
    return InlineKeyboardMarkup(keyboard)