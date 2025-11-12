import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8366585450:AAGoY_-J7SQh7pMtlEYeQvXwVmXFUChrgdY")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "7991318409"))

# Exchange Rate Configuration
EXCHANGE_RATE_EUR_TO_USD = 1.16  # Default exchange rate
