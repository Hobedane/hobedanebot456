import os
from dotenv import load_dotenv

load_dotenv()

# Bot token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Admin user IDs (replace with your actual admin IDs)
ADMINS = [123456789]  # Replace with your Telegram user ID

# Database configuration
DATABASE_NAME = 'bot_database.db'

# Payment configuration
CRYPTO_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # Example Bitcoin address
BANK_ACCOUNT = "123456789"
BANK_NAME = "Example Bank"
PAYPAL_EMAIL = "paypal@example.com"

# Other settings
DEFAULT_EXCHANGE_RATE = 1.07
