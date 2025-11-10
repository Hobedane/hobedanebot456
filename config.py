import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///shop.db')
EXCHANGE_RATE = float(os.getenv('EXCHANGE_RATE', 1.08))

# Default messages that can be customized via admin panel
DEFAULT_MESSAGES = {
    'welcome': "Welcome to our shop! 🛍️",
    'success_payment': "✅ Payment confirmed! Your products have been delivered.",
    'rules': "📋 Shop Rules:\n1. All sales are final\n2. No refunds\n3. Contact admin for issues",
    'added_to_cart': "✅ Added to cart!",
    'payment_instructions': "Please send exactly {amount} {currency} to:\n`{address}`\n\nAfter sending, click 'Paid' and enter your source address.",
}