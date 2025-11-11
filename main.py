import logging
from telegram import Update
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

# Import admin sub-handlers
from handlers.admin_products import admin_products, admin_edit_product, admin_add_product_start
from handlers.admin_payments import admin_payments, edit_payment_start, remove_payment_start, add_new_crypto
from handlers.admin_content import admin_content, admin_edit_content_start, admin_edit_success_message
from handlers.admin_discounts import admin_discounts, admin_add_client_discount, admin_add_general_discount, view_all_discounts
from handlers.admin_stats import admin_stats

# Import payment approval
from handlers.payment_approval import (
    admin_approve_payment, admin_reject_payment, 
    confirm_approve_payment, cancel_approve_payment,
    confirm_reject_payment, cancel_reject_payment
)

# Unified message handler
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text
    
    # KÕIGEPEALT kontrolli content editing - SEE ON OLULINE!
    if 'editing_content' in context.user_data:
        from handlers.admin_content import handle_content_edit
        await handle_content_edit(update, context)
        return
    
    # Siis kontrolli payment editing
    if 'editing_payment' in context.user_data:
        from handlers.admin_payments import handle_payment_edit
        await handle_payment_edit(update, context)
        return
    
    # Siis kontrolli discount code waiting (KLIENDI POOLNE)
    if context.user_data.get('waiting_discount_code'):
        await handle_discount_code_input(update, context)
        return
    
    # Siis kontrolli payment source address waiting
    if context.user_data.get('waiting_payment_source'):
        await handle_payment_source(update, context)
        return
    
    # ALLES NÜÜD kontrolli admin mode'e - SEE ON PARANDUS!
    admin_mode = context.user_data.get('admin_mode')
    
    if admin_mode == 'updating_exchange_rate':
        await handle_exchange_rate_update(update, context)
        return
    elif admin_mode == 'adding_crypto_type':
        from handlers.admin_payments import handle_crypto_type
        await handle_crypto_type(update, context)
        return
    elif admin_mode == 'adding_crypto_address':
        from handlers.admin_payments import handle_crypto_address
        await handle_crypto_address(update, context)
        return
    elif admin_mode == 'adding_crypto_blockchain':
        from handlers.admin_payments import handle_crypto_blockchain
        await handle_crypto_blockchain(update, context)
        return
    elif admin_mode == 'adding_client_discount_id':
        from handlers.admin_discounts import handle_client_discount_identifier
        await handle_client_discount_identifier(update, context)
        return
    elif admin_mode == 'adding_discount_code':
        from handlers.admin_discounts import handle_discount_code_input_admin
        await handle_discount_code_input_admin(update, context)
        return
    elif admin_mode == 'adding_discount_percent':
        from handlers.admin_discounts import handle_discount_percent
        await handle_discount_percent(update, context)
        return
    elif admin_mode == 'adding_discount_expiry':
        from handlers.admin_discounts import handle_discount_expiry
        await handle_discount_expiry(update, context)
        return
    elif admin_mode == 'adding_discount_max_uses':
        from handlers.admin_discounts import handle_discount_max_uses
        await handle_discount_max_uses(update, context)
        return
    elif admin_mode == 'adding_product_name':
        from handlers.admin_products import handle_product_name
        await handle_product_name(update, context)
        return
    elif admin_mode == 'adding_product_price':
        from handlers.admin_products import handle_product_price
        await handle_product_price(update, context)
        return
    elif admin_mode == 'adding_product_description':
        from handlers.admin_products import handle_product_description
        await handle_product_description(update, context)
        return
    elif admin_mode == 'adding_product_quantity':
        from handlers.admin_products import handle_product_quantity
        await handle_product_quantity(update, context)
        return
    elif admin_mode == 'adding_product_image1':
        from handlers.admin_products import handle_product_image1
        await handle_product_image1(update, context)
        return
    elif admin_mode == 'adding_product_image2_choice':
        from handlers.admin_products import handle_image2_choice
        await handle_image2_choice(update, context)
        return
    elif admin_mode == 'adding_product_image2':
        from handlers.admin_products import handle_product_image2
        await handle_product_image2(update, context)
        return
    elif admin_mode == 'adding_product_coordinates':
        from handlers.admin_products import handle_product_coordinates
        await handle_product_coordinates(update, context)
        return
    
    # If no specific handler, send to main menu
    await start(update, context)

# Product image handler
async def handle_product_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ühendatud pildihandler kõikidele piltidele"""
    if update.message.photo:
        # Check if we're in product image adding mode
        admin_mode = context.user_data.get('admin_mode')
        
        if admin_mode == 'adding_product_image1':
            from handlers.admin_products import handle_product_image1
            await handle_product_image1(update, context)
        elif admin_mode == 'adding_product_image2':
            from handlers.admin_products import handle_product_image2
            await handle_product_image2(update, context)
        else:
            await update.message.reply_text("✅ Image received! But I'm not sure what to do with it.")

def main() -> None:
    # Initialize database
    init_database()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # ========== KLIENDI HANDLERID ==========
    
    # Products and cart
    application.add_handler(CallbackQueryHandler(show_products, pattern="^view_products$"))
    application.add_handler(CallbackQueryHandler(show_product_detail, pattern="^product_"))
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_to_cart_"))
    application.add_handler(CallbackQueryHandler(buy_now, pattern="^buy_now_"))
    application.add_handler(CallbackQueryHandler(view_cart, pattern="^view_cart$"))
    application.add_handler(CallbackQueryHandler(clear_cart, pattern="^clear_cart$"))
    application.add_handler(CallbackQueryHandler(checkout_cart, pattern="^checkout_cart$"))
    
    # Payment process (KLIENDI poolne)
    application.add_handler(CallbackQueryHandler(show_payment_options, pattern="^show_payment_options$"))
    application.add_handler(CallbackQueryHandler(show_payment_details, pattern="^payment_"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="^confirm_payment$"))
    
    # Discount code handlers (KLIENDI poolne)
    application.add_handler(CallbackQueryHandler(no_discount_code, pattern="^no_discount_code$"))
    application.add_handler(CallbackQueryHandler(proceed_to_payment, pattern="^proceed_to_payment$"))
    
    # Content pages handlers
    application.add_handler(CallbackQueryHandler(about_us, pattern="^about_us$"))
    application.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))
    application.add_handler(CallbackQueryHandler(website, pattern="^website$"))
    application.add_handler(CallbackQueryHandler(rules, pattern="^rules$"))
    application.add_handler(CallbackQueryHandler(faq, pattern="^faq$"))
    
    # ========== ADMINI HANDLERID ==========
    
    # Admin panel handlers
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_exchange_rate, pattern="^admin_exchange_rate$"))
    
    # Admin sub-menu handlers
    application.add_handler(CallbackQueryHandler(admin_products, pattern="^admin_products$"))
    application.add_handler(CallbackQueryHandler(admin_payments, pattern="^admin_payments$"))
    application.add_handler(CallbackQueryHandler(admin_content, pattern="^admin_content$"))
    application.add_handler(CallbackQueryHandler(admin_discounts, pattern="^admin_discounts$"))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    
    # Admin content management
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_welcome_message$"))
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_about_us$"))
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_contact$"))
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_website$"))
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_rules$"))
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_faq$"))
    application.add_handler(CallbackQueryHandler(admin_edit_success_message, pattern="^admin_edit_success_message$"))
    
    # Admin discount management
    application.add_handler(CallbackQueryHandler(admin_add_client_discount, pattern="^add_client_discount$"))
    application.add_handler(CallbackQueryHandler(admin_add_general_discount, pattern="^add_general_discount$"))
    application.add_handler(CallbackQueryHandler(view_all_discounts, pattern="^view_all_discounts$"))
    
    # Admin payment management (MAKSEVIISIDE HALDUS)
    application.add_handler(CallbackQueryHandler(edit_payment_start, pattern="^edit_payment_"))
    application.add_handler(CallbackQueryHandler(remove_payment_start, pattern="^remove_payment_"))
    application.add_handler(CallbackQueryHandler(add_new_crypto, pattern="^add_new_crypto$"))
    
    # Admin product management
    application.add_handler(CallbackQueryHandler(admin_edit_product, pattern="^admin_edit_product_"))
    application.add_handler(CallbackQueryHandler(admin_add_product_start, pattern="^admin_add_product$"))
    
    # Admin payment approval (MAKSE KINNITAMINE)
    application.add_handler(CallbackQueryHandler(admin_approve_payment, pattern="^approve_"))
    application.add_handler(CallbackQueryHandler(admin_reject_payment, pattern="^reject_"))
    application.add_handler(CallbackQueryHandler(confirm_approve_payment, pattern="^confirm_approve_"))
    application.add_handler(CallbackQueryHandler(cancel_approve_payment, pattern="^cancel_approve_"))
    application.add_handler(CallbackQueryHandler(confirm_reject_payment, pattern="^confirm_reject_"))
    application.add_handler(CallbackQueryHandler(cancel_reject_payment, pattern="^cancel_reject_"))
    
    # Payment removal confirmation
    application.add_handler(CallbackQueryHandler(confirm_remove_payment, pattern="^confirm_remove_"))
    
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
