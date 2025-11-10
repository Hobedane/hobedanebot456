from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import config
from database import init_db

# Import handlers
from handlers.start import start, show_rules, show_about
from handlers.products import show_products, view_product, add_to_cart
from handlers.cart import show_cart, enter_discount_code, process_discount_code, clear_cart
from handlers.payments import checkout, select_crypto, confirm_payment, enter_source_address, process_source_address
from handlers.admin import admin_panel, admin_products, admin_crypto, admin_stats, admin_payments, confirm_order, final_confirm_order
from handlers.discounts import admin_discounts, create_discount, process_discount_creation
from handlers.content import admin_messages, edit_message, process_message_update
from handlers.message_handler import admin_send_message, process_message_sending

# Conversation states
WAITING_DISCOUNT_CODE, WAITING_SOURCE_ADDRESS, WAITING_MESSAGE_UPDATE, WAITING_MESSAGE_DETAILS, WAITING_DISCOUNT_DETAILS = range(5)

async def main_menu(update: Update, context):
    from utils.helpers import get_main_keyboard
    await update.callback_query.edit_message_text(
        "Main Menu",
        reply_markup=get_main_keyboard()
    )

def main():
    # Initialize database
    init_db()
    
    # Create application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # Main menu callbacks
    application.add_handler(CallbackQueryHandler(show_products, pattern="^products$"))
    application.add_handler(CallbackQueryHandler(show_cart, pattern="^cart$"))
    application.add_handler(CallbackQueryHandler(show_rules, pattern="^rules$"))
    application.add_handler(CallbackQueryHandler(show_about, pattern="^about$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    
    # Products callbacks
    application.add_handler(CallbackQueryHandler(view_product, pattern="^view_product_"))
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_cart_"))
    
    # Cart callbacks
    application.add_handler(CallbackQueryHandler(checkout, pattern="^checkout$"))
    application.add_handler(CallbackQueryHandler(enter_discount_code, pattern="^enter_discount$"))
    application.add_handler(CallbackQueryHandler(clear_cart, pattern="^clear_cart$"))
    
    # Payment callbacks
    application.add_handler(CallbackQueryHandler(select_crypto, pattern="^select_crypto_"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="^confirm_payment_"))
    application.add_handler(CallbackQueryHandler(enter_source_address, pattern="^enter_source_"))
    
    # Admin callbacks
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_products, pattern="^admin_products$"))
    application.add_handler(CallbackQueryHandler(admin_crypto, pattern="^admin_crypto$"))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_payments, pattern="^admin_payments$"))
    application.add_handler(CallbackQueryHandler(admin_discounts, pattern="^admin_discounts$"))
    application.add_handler(CallbackQueryHandler(admin_messages, pattern="^admin_messages$"))
    application.add_handler(CallbackQueryHandler(admin_send_message, pattern="^admin_send_msg$"))
    application.add_handler(CallbackQueryHandler(confirm_order, pattern="^confirm_order_"))
    application.add_handler(CallbackQueryHandler(final_confirm_order, pattern="^final_confirm_"))
    application.add_handler(CallbackQueryHandler(edit_message, pattern="^edit_message_"))
    application.add_handler(CallbackQueryHandler(create_discount, pattern="^create_discount$"))
    
    # Conversation handlers
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(enter_discount_code, pattern="^enter_discount$"),
            CallbackQueryHandler(enter_source_address, pattern="^enter_source_"),
            CallbackQueryHandler(edit_message, pattern="^edit_message_"),
            CallbackQueryHandler(admin_send_message, pattern="^admin_send_msg$"),
            CallbackQueryHandler(create_discount, pattern="^create_discount$")
        ],
        states={
            WAITING_DISCOUNT_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_discount_code)
            ],
            WAITING_SOURCE_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_source_address)
            ],
            WAITING_MESSAGE_UPDATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_message_update)
            ],
            WAITING_MESSAGE_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_message_sending)
            ],
            WAITING_DISCOUNT_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_discount_creation)
            ],
        },
        fallbacks=[CallbackQueryHandler(main_menu, pattern="^main_menu$")]
    )
    application.add_handler(conv_handler)
    
    # Start the bot
    print("Bot started!")
    application.run_polling()

if __name__ == "__main__":
    main()