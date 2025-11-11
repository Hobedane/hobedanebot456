import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN

# Import handlers
from handlers.start import start
from handlers.products import products
from handlers.cart import cart, checkout
from handlers.discounts import apply_discount
from handlers.payments import payment_methods, process_payment
from handlers.content import welcome_message, success_message

# Admin handlers
from handlers.admin import admin, admin_exchange_rate, admin_stats, admin_payment_settings, handle_exchange_rate_input, set_exchange_rate
from handlers.admin_products import admin_products, add_product_start, add_product_name, add_product_description, add_product_price, add_product_image, add_second_image_handler, add_second_image_input, add_product_confirm, add_product_confirm_callback, view_products, delete_product_start, delete_product_confirm, cancel_product
from handlers.admin_discounts import admin_discounts, add_discount_start, add_discount_code, add_discount_percentage, add_discount_max_uses, add_discount_confirm, view_discounts, cancel_discount
from handlers.admin_content import admin_content, content_success, content_success_input, content_welcome, content_welcome_input, cancel_content
from handlers.admin_payments import admin_payments, toggle_payment
from handlers.admin_stats import admin_stats as admin_stats_handler

# Initialize database
from database import init_db

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    # Initialize database
    init_db()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Basic commands
    application.add_handler(CommandHandler("start", start))
    
    # Product handlers
    application.add_handler(CallbackQueryHandler(products, pattern='^products$'))
    application.add_handler(CallbackQueryHandler(cart, pattern='^cart$'))
    application.add_handler(CallbackQueryHandler(checkout, pattern='^checkout$'))
    
    # Discount handlers
    application.add_handler(CallbackQueryHandler(apply_discount, pattern='^apply_discount$'))
    
    # Payment handlers
    application.add_handler(CallbackQueryHandler(payment_methods, pattern='^payment_methods$'))
    application.add_handler(CallbackQueryHandler(process_payment, pattern='^process_payment_'))
    
    # Content handlers
    application.add_handler(CallbackQueryHandler(welcome_message, pattern='^welcome_message$'))
    application.add_handler(CallbackQueryHandler(success_message, pattern='^success_message$'))
    
    # Admin handlers
    application.add_handler(CallbackQueryHandler(admin, pattern='^admin$'))
    application.add_handler(CallbackQueryHandler(admin_exchange_rate, pattern='^admin_exchange_rate$'))
    application.add_handler(CallbackQueryHandler(set_exchange_rate, pattern='^set_exchange_rate$'))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern='^admin_stats$'))
    application.add_handler(CallbackQueryHandler(admin_payment_settings, pattern='^admin_payment_settings$'))
    application.add_handler(CallbackQueryHandler(admin_products, pattern='^admin_products$'))
    application.add_handler(CallbackQueryHandler(admin_discounts, pattern='^admin_discounts$'))
    application.add_handler(CallbackQueryHandler(view_discounts, pattern='^view_discounts$'))
    application.add_handler(CallbackQueryHandler(admin_content, pattern='^admin_content$'))
    application.add_handler(CallbackQueryHandler(admin_payments, pattern='^admin_payments$'))
    application.add_handler(CallbackQueryHandler(toggle_payment, pattern='^toggle_payment_'))
    application.add_handler(CallbackQueryHandler(view_products, pattern='^view_products$'))
    application.add_handler(CallbackQueryHandler(delete_product_start, pattern='^delete_product$'))
    application.add_handler(CallbackQueryHandler(delete_product_confirm, pattern='^delete_product_'))
    
    # Exchange rate input handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_exchange_rate_input
    ))
    
    # Conversation handler for adding products
    product_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_product_start, pattern='^add_product$')],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_description)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
            3: [MessageHandler(filters.PHOTO, add_product_image)],
            4: [
                CallbackQueryHandler(add_second_image_handler, pattern='^(add_second_image|skip_second_image)$'),
                MessageHandler(filters.PHOTO, add_second_image_input)
            ],
            5: [CallbackQueryHandler(add_product_confirm_callback, pattern='^(confirm_product|cancel_product)$')]
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
    application.run_polling()

if __name__ == '__main__':
    main()
