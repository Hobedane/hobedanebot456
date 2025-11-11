import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []
DATABASE = 'shop_bot.db'

# Payment configuration (if using any payment gateway)
PAYMENT_PROVIDER = os.getenv('PAYMENT_PROVIDER', '')
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN', '')

# Conversation states
(
    START, ADMIN, PRODUCTS, CART, DISCOUNTS, PAYMENTS, CONTENT, STATS,
    PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_DESCRIPTION, PRODUCT_QUANTITY, PRODUCT_IMAGE, CONFIRM_ADD_PRODUCT,
    PRODUCT_SECOND_IMAGE, PRODUCT_COORDINATES
) = range(16)

# Admin states
ADMIN_PRODUCTS = "admin_products"

# Logging configuration
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
