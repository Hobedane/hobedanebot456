from config import ADMIN_USER_ID
from database import get_exchange_rate

def is_admin(user_id):
    return user_id == ADMIN_USER_ID

def convert_eur_to_usd(eur_amount):
    """Convert EUR amount to USD using current exchange rate"""
    rate = get_exchange_rate()
    return round(eur_amount * rate, 2)

def format_price_display(eur_price):
    """Format price display with both EUR and USD"""
    usd_price = convert_eur_to_usd(eur_price)
    return f"{eur_price}€ / ${usd_price} USD"
