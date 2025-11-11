import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN

# Import handlers
from handlers.start import start, about
from handlers.products import products, view_product, add_to_cart_handler
from handlers.cart import cart, clear_cart_handler, checkout
from handlers.discounts import apply_discount, apply_discount_callback
from handlers.payments import payment_methods, process_payment
from handlers.content import welcome_message, success_message

# Admin handlers
from handlers.admin import admin, admin_exchange_rate, admin_stats, admin_back, set_exchange_rate, handle_exchange_rate_input
from handlers.admin_products import (
    admin_products, add_product_start, add_product_name, add_product_description, 
    add_product_price, add_product_stock, add_product_image, add_second_image_handler, 
    add_second_image_input, add_product_location, add_product_confirm, 
    add_product_confirm_callback, view_products, delete_product_start, 
    delete_product_confirm, cancel_product
)
from handlers.admin_discounts import (
    admin_discounts, add_discount_start, add_discount_code, add_discount_percentage, 
    add_discount_max_uses, add_discount_confirm, view_discounts, cancel_discount
)
from handlers.admin_content import (
    admin_content, content_success, content_success_input, content_welcome, 
    content_welcome_input, cancel_content
)
from handlers.admin_payments import admin_payments, toggle_payment
from handlers.admin_stats import admin_stats as admin_stats_detailed
from handlers.payment_approval import payment_approval

# Database
from database import init_db, add_user

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import states from admin_products
from handlers.admin_products import (
    PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_PRICE, PRODUCT_STOCK, 
    PRODUCT_IMAGE, PRODUCT_SECOND_IMAGE, PRODUCT_LOCATION, PRODUCT_CONFIRM
)

async def start_command(update: Update, context: CallbackContext) -> None:
    """Handle /start command"""
    user = update.effective_user
    add_user(user.id, user.username, user.first_name, user.last_name)
    await start(update, context)

def main() -> None:
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Basic commands
    application.add_handler(CommandHandler("start", start_command))
    
    # Product handlers
    application.add_handler(CallbackQueryHandler(products, pattern='^products$'))
    application.add_handler(CallbackQueryHandler(view_product, pattern='^view_product_'))
    application.add_handler(CallbackQueryHandler(add_to_cart_handler, pattern='^add_to_cart_'))
    
    # Cart handlers
    application.add_handler(CallbackQueryHandler(cart, pattern='^cart$'))
    application.add_handler(CallbackQueryHandler(clear_cart_handler, pattern='^clear_cart$'))
    application.add_handler(CallbackQueryHandler(checkout, pattern='^checkout$'))
    
    # Discount handlers
    application.add_handler(CallbackQueryHandler(apply_discount, pattern='^apply_discount$'))
    application.add_handler(CallbackQueryHandler(apply_discount_callback, pattern='^apply_discount_'))
    
    # Payment handlers
    application.add_handler(CallbackQueryHandler(payment_methods, pattern='^payment_methods$'))
    application.add_handler(CallbackQueryHandler(process_payment, pattern='^process_payment_'))
    application.add_handler(CallbackQueryHandler(payment_approval, pattern='^payment_approval_'))
    
    # Content handlers
    application.add_handler(CallbackQueryHandler(welcome_message, pattern='^welcome_message$'))
    application.add_handler(CallbackQueryHandler(success_message, pattern='^success_message$'))
    application.add_handler(CallbackQueryHandler(about, pattern='^about$'))
    
    # Admin handlers
    application.add_handler(CallbackQueryHandler(admin, pattern='^admin$'))
    application.add_handler(CallbackQueryHandler(admin_back, pattern='^admin_back$'))
    application.add_handler(CallbackQueryHandler(admin_products, pattern='^admin_products$'))
    application.add_handler(CallbackQueryHandler(admin_discounts, pattern='^admin_discounts$'))
    application.add_handler(CallbackQueryHandler(admin_content, pattern='^admin_content$'))
    application.add_handler(CallbackQueryHandler(admin_payments, pattern='^admin_payments$'))
    application.add_handler(CallbackQueryHandler(admin_exchange_rate, pattern='^admin_exchange_rate$'))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern='^admin_stats$'))
    application.add_handler(CallbackQueryHandler(admin_stats_detailed, pattern='^admin_stats_detailed$'))
    application.add_handler(CallbackQueryHandler(set_exchange_rate, pattern='^set_exchange_rate$'))
    application.add_handler(CallbackQueryHandler(toggle_payment, pattern='^toggle_payment_'))
    application.add_handler(CallbackQueryHandler(view_products, pattern='^view_products$'))
    application.add_handler(CallbackQueryHandler(view_discounts, pattern='^view_discounts$'))
    application.add_handler(CallbackQueryHandler(delete_product_start, pattern='^delete_product$'))
    application.add_handler(CallbackQueryHandler(delete_product_confirm, pattern='^delete_product_'))
    
    # Exchange rate input handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_exchange_rate_input
    ))
    
    # Discount input handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        apply_discount_callback
    ))
    
    # Conversation handler for adding products
    product_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_product_start, pattern='^add_product$')],
        states={
            PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name)],
            PRODUCT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_description)],
            PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
            PRODUCT_STOCK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_stock)],
            PRODUCT_IMAGE: [MessageHandler(filters.PHOTO, add_product_image)],
            PRODUCT_SECOND_IMAGE: [
                CallbackQueryHandler(add_second_image_handler, pattern='^(add_second_image|skip_second_image)$'),
                MessageHandler(filters.PHOTO, add_second_image_input)
            ],
            PRODUCT_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_location)],
            PRODUCT_CONFIRM: [CallbackQueryHandler(add_product_confirm_callback, pattern='^(confirm_product|cancel_product)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel_product)]
    )
    application.add_handler(product_conv_handler)
    
    # Conversation handler for adding discounts
    discount_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_discount_start, pattern='^add_discount$')],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_discount_code)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_discount_percentage)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_discount_max_uses)],
            3: [CallbackQueryHandler(add_discount_confirm, pattern='^(confirm_discount|cancel_discount)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel_discount)]
    )
    application.add_handler(discount_conv_handler)
    
    # Conversation handler for content management
    content_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(content_success, pattern='^content_success$'),
            CallbackQueryHandler(content_welcome, pattern='^content_welcome$')
        ],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, content_success_input)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, content_welcome_input)]
        },
        fallbacks=[CommandHandler('cancel', cancel_content)]
    )
    application.add_handler(content_conv_handler)

    # Start the Bot
    logger.info("Bot starting...")
    application.run_polling()
    logger.info("Bot stopped")

if __name__ == '__main__':
    main()
