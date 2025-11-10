from config import ADMIN_USER_ID
from database import get_exchange_rate

def is_admin(user_id):
    return user_id == ADMIN_USER_ID

def convert_eur_to_usd(amount_eur):
    """Convert EUR amount to USD using current exchange rate"""
    rate = get_exchange_rate()
    return round(amount_eur * rate, 2)

def format_price_display(amount_eur):
    """Format price display with both EUR and USD"""
    amount_usd = convert_eur_to_usd(amount_eur)
    return f"{amount_eur}€ (${amount_usd})"
