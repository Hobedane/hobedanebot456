import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# Import configurations
from config import BOT_TOKEN, logger
from database import init_database

# Import handlers
from handlers.start import start, back_to_main
from handlers.products import show_products, show_product_detail, buy_now
from handlers.cart import add_to_cart, view_cart, clear_cart, checkout_cart
from handlers.payment import show_payment_options, show_payment_details, confirm_payment, handle_payment_source
from handlers.admin import admin_panel, admin_exchange_rate, handle_exchange_rate_update
from handlers.content import about_us, contact, website, rules, faq
from handlers.discount import ask_discount_code, no_discount_code, proceed_to_payment, handle_discount_code_input

# Unified message handler
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check for discount code waiting (KLIENDI POOLNE)
    if context.user_data.get('waiting_discount_code'):
        await handle_discount_code_input(update, context)
        return
    
    # Check for payment source address waiting
    if context.user_data.get('waiting_payment_source'):
        await handle_payment_source(update, context)
        return
    
    # Check admin modes
    admin_mode = context.user_data.get('admin_mode')
    if admin_mode == 'updating_exchange_rate':
        await handle_exchange_rate_update(update, context)
        return
    
    # If no specific handler, send to main menu
    await start(update, context)

# Product image handler
async def handle_product_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ühendatud pildihandler kõikidele piltidele"""
    # This would handle product images - implementation depends on your specific needs
    if update.message.photo:
        await update.message.reply_text("✅ Image received!")

def main() -> None:
    # Initialize database
    init_database()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(show_products, pattern="^view_products$"))
    application.add_handler(CallbackQueryHandler(show_product_detail, pattern="^product_"))
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_to_cart_"))
    application.add_handler(CallbackQueryHandler(buy_now, pattern="^buy_now_"))
    application.add_handler(CallbackQueryHandler(view_cart, pattern="^view_cart$"))
    application.add_handler(CallbackQueryHandler(clear_cart, pattern="^clear_cart$"))
    application.add_handler(CallbackQueryHandler(checkout_cart, pattern="^checkout_cart$"))
    application.add_handler(CallbackQueryHandler(show_payment_options, pattern="^show_payment_options$"))
    application.add_handler(CallbackQueryHandler(show_payment_details, pattern="^payment_"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="^confirm_payment$"))
    
    # Discount code handlers
    application.add_handler(CallbackQueryHandler(no_discount_code, pattern="^no_discount_code$"))
    application.add_handler(CallbackQueryHandler(proceed_to_payment, pattern="^proceed_to_payment$"))
    
    # Content pages handlers
    application.add_handler(CallbackQueryHandler(about_us, pattern="^about_us$"))
    application.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))
    application.add_handler(CallbackQueryHandler(website, pattern="^website$"))
    application.add_handler(CallbackQueryHandler(rules, pattern="^rules$"))
    application.add_handler(CallbackQueryHandler(faq, pattern="^faq$"))
    
    # Admin panel handlers
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_exchange_rate, pattern="^admin_exchange_rate$"))
    
    # Back handler
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    
    # Unified text handler - PEAB OLEMA VIIMANE
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_all_messages
    ))
    
    # Image handler
    application.add_handler(MessageHandler(filters.PHOTO, handle_product_image))
    
    # Start bot
    print("🚀 Bot starting...")
    application.run_polling()
    print("✅ Bot is running!")

if __name__ == "__main__":
    main()
