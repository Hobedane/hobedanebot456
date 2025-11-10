import logging

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8366585450:AAGoY_-J7SQh7pMtlEYeQvXwVmXFUChrgdY"
ADMIN_USER_ID = 7991318409

# Exchange rate (manual)
EXCHANGE_RATE_EUR_TO_USD = 1.16  # Default value, can be changed via admin
