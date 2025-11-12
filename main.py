import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# Import handlers
from handlers.start import start, back_to_main
from handlers.products import show_products, show_product_detail
from handlers.cart import add_to_cart, view_cart, clear_cart
from handlers.discounts import ask_discount_code, handle_discount_code_input, no_discount_code, proceed_to_payment
from handlers.payments import buy_now, checkout_cart, show_payment_options, show_payment_details, confirm_payment
from handlers.content import about_us, contact, website, rules, faq
from handlers.admin import admin_panel
from handlers.payment_approval import (
    admin_approve_payment, admin_reject_payment, 
    confirm_approve_payment, cancel_approve_payment,
    confirm_reject_payment, cancel_reject_payment
)
from handlers.admin_content import admin_content, admin_edit_content_start, admin_edit_success_message
from handlers.admin_discounts import (
    admin_discounts, admin_add_client_discount, admin_add_general_discount, 
    view_all_discounts
)
from handlers.admin_payments import (
    admin_payments, edit_payment_start, remove_payment_start, 
    confirm_remove_payment, add_new_crypto
)
from handlers.admin_products import (
    admin_products, admin_edit_product, admin_add_product_start,
    edit_product_name, edit_product_price, edit_product_description, edit_product_quantity,
    edit_product_coordinates, edit_product_image1, edit_product_image2,
    toggle_product_active, delete_product, confirm_delete_product
)
from handlers.admin_stats import admin_stats
from handlers.admin_exchange_rate import admin_exchange_rate

# Import database and config
from database import init_database
from config import BOT_TOKEN

# Import message handlers
from handlers.admin_products import (
    handle_product_name, handle_product_price, handle_product_description, 
    handle_product_quantity, handle_product_image, handle_product_coordinates,
    handle_product_field_edit, handle_image2_choice
)
from handlers.admin_payments import (
    handle_crypto_type, handle_crypto_address, handle_crypto_blockchain,
    handle_payment_edit
)
from handlers.admin_discounts import (
    handle_client_discount_id, handle_discount_code_input_admin,
    handle_discount_percent, handle_discount_expiry, handle_discount_max_uses
)
from handlers.admin_content import handle_content_edit
from handlers.admin_exchange_rate import handle_exchange_rate_edit
from handlers.payments import handle_payment_source

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    # Initialize database
    init_database()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("skip", handle_product_coordinates))
    
    # Callback handlers - ALL BUTTONS PROPERLY REGISTERED
    
    # Product handlers
    application.add_handler(CallbackQueryHandler(show_products, pattern="^view_products$"))
    application.add_handler(CallbackQueryHandler(show_product_detail, pattern="^product_"))
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_to_cart_"))
    application.add_handler(CallbackQueryHandler(buy_now, pattern="^buy_now_"))
    
    # Cart handlers
    application.add_handler(CallbackQueryHandler(view_cart, pattern="^view_cart$"))
    application.add_handler(CallbackQueryHandler(clear_cart, pattern="^clear_cart$"))
    application.add_handler(CallbackQueryHandler(checkout_cart, pattern="^checkout_cart$"))
    
    # Payment handlers
    application.add_handler(CallbackQueryHandler(show_payment_options, pattern="^show_payment_options$"))
    application.add_handler(CallbackQueryHandler(show_payment_details, pattern="^payment_"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="^confirm_payment$"))
    
    # Discount handlers
    application.add_handler(CallbackQueryHandler(no_discount_code, pattern="^no_discount_code$"))
    application.add_handler(CallbackQueryHandler(proceed_to_payment, pattern="^proceed_to_payment$"))
    
    # Admin payment approval handlers
    application.add_handler(CallbackQueryHandler(admin_approve_payment, pattern="^approve_"))
    application.add_handler(CallbackQueryHandler(admin_reject_payment, pattern="^reject_"))
    application.add_handler(CallbackQueryHandler(confirm_approve_payment, pattern="^confirm_approve_"))
    application.add_handler(CallbackQueryHandler(cancel_approve_payment, pattern="^cancel_approve_"))
    application.add_handler(CallbackQueryHandler(confirm_reject_payment, pattern="^confirm_reject_"))
    application.add_handler(CallbackQueryHandler(cancel_reject_payment, pattern="^cancel_reject_"))
    
    # Content page handlers
    application.add_handler(CallbackQueryHandler(about_us, pattern="^about_us$"))
    application.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))
    application.add_handler(CallbackQueryHandler(website, pattern="^website$"))
    application.add_handler(CallbackQueryHandler(rules, pattern="^rules$"))
    application.add_handler(CallbackQueryHandler(faq, pattern="^faq$"))
    
    # Admin panel handlers
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_content, pattern="^admin_content$"))
    application.add_handler(CallbackQueryHandler(admin_discounts, pattern="^admin_discounts$"))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_exchange_rate, pattern="^admin_exchange_rate$"))
    
    # Product management handlers
    application.add_handler(CallbackQueryHandler(admin_products, pattern="^admin_products$"))
    application.add_handler(CallbackQueryHandler(admin_edit_product, pattern="^admin_edit_product_"))
    application.add_handler(CallbackQueryHandler(admin_add_product_start, pattern="^admin_add_product$"))
    application.add_handler(CallbackQueryHandler(delete_product, pattern="^delete_product_"))
    application.add_handler(CallbackQueryHandler(confirm_delete_product, pattern="^confirm_delete_"))
    
    # Product editing handlers
    application.add_handler(CallbackQueryHandler(edit_product_name, pattern="^edit_name_"))
    application.add_handler(CallbackQueryHandler(edit_product_price, pattern="^edit_price_"))
    application.add_handler(CallbackQueryHandler(edit_product_description, pattern="^edit_desc_"))
    application.add_handler(CallbackQueryHandler(edit_product_quantity, pattern="^edit_quantity_"))
    application.add_handler(CallbackQueryHandler(edit_product_coordinates, pattern="^edit_coords_"))
    application.add_handler(CallbackQueryHandler(edit_product_image1, pattern="^edit_image1_"))
    application.add_handler(CallbackQueryHandler(edit_product_image2, pattern="^edit_image2_"))
    application.add_handler(CallbackQueryHandler(toggle_product_active, pattern="^toggle_active_"))
    
    # Payment settings handlers
    application.add_handler(CallbackQueryHandler(admin_payments, pattern="^admin_payments$"))
    application.add_handler(CallbackQueryHandler(remove_payment_start, pattern="^remove_payment_"))
    application.add_handler(CallbackQueryHandler(confirm_remove_payment, pattern="^confirm_remove_"))
    application.add_handler(CallbackQueryHandler(edit_payment_start, pattern="^edit_payment_"))
    application.add_handler(CallbackQueryHandler(add_new_crypto, pattern="^add_new_crypto$"))
    
    # Content management handlers
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_welcome_message$"))
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_about_us$"))
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_contact$"))
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_website$"))
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_rules$"))
    application.add_handler(CallbackQueryHandler(admin_edit_content_start, pattern="^admin_edit_faq$"))
    application.add_handler(CallbackQueryHandler(admin_edit_success_message, pattern="^admin_edit_success_message$"))
    
    # Discount management handlers
    application.add_handler(CallbackQueryHandler(admin_add_client_discount, pattern="^add_client_discount$"))
    application.add_handler(CallbackQueryHandler(admin_add_general_discount, pattern="^add_general_discount$"))
    application.add_handler(CallbackQueryHandler(view_all_discounts, pattern="^view_all_discounts$"))
    
    # Back handler
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    
    # Unified text handler - MUST BE LAST
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_all_messages
    ))
    
    # Single image handler for all photos
    application.add_handler(MessageHandler(filters.PHOTO, handle_product_image))
    
    # Start bot
    print("🚀 Bot starting...")
    application.run_polling()
    print("✅ Bot is running!")

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check for discount code waiting (CLIENT SIDE)
    if context.user_data.get('waiting_discount_code'):
        await handle_discount_code_input(update, context)
        return
    
    # Check for payment source address waiting
    if context.user_data.get('waiting_payment_source'):
        await handle_payment_source(update, context)
        return
    
    # Check for product field editing
    if 'editing_product_id' in context.user_data and 'editing_field' in context.user_data:
        await handle_product_field_edit(update, context)
        return
    
    # Check admin modes
    admin_mode = context.user_data.get('admin_mode')
    
    if admin_mode == 'adding_product_name':
        await handle_product_name(update, context)
    elif admin_mode == 'adding_product_price':
        await handle_product_price(update, context)
    elif admin_mode == 'adding_product_description':
        await handle_product_description(update, context)
    elif admin_mode == 'adding_product_quantity':
        await handle_product_quantity(update, context)
    elif admin_mode == 'adding_product_image2_choice':
        await handle_image2_choice(update, context)
    elif admin_mode == 'adding_product_coordinates':
        await handle_product_coordinates(update, context)
    elif admin_mode == 'adding_crypto_type':
        await handle_crypto_type(update, context)
    elif admin_mode == 'adding_crypto_address':
        await handle_crypto_address(update, context)
    elif admin_mode == 'adding_crypto_blockchain':
        await handle_crypto_blockchain(update, context)
    elif admin_mode == 'adding_client_discount_id':
        await handle_client_discount_id(update, context)
    elif admin_mode == 'adding_discount_code':
        await handle_discount_code_input_admin(update, context)
    elif admin_mode == 'adding_discount_percent':
        await handle_discount_percent(update, context)
    elif admin_mode == 'adding_discount_expiry':
        await handle_discount_expiry(update, context)
    elif admin_mode == 'adding_discount_max_uses':
        await handle_discount_max_uses(update, context)
    elif admin_mode == 'editing_exchange_rate':
        await handle_exchange_rate_edit(update, context)
    
    # Check content editing mode
    elif 'editing_content' in context.user_data:
        await handle_content_edit(update, context)
    
    # Check payment address editing mode
    elif 'editing_payment' in context.user_data:
        await handle_payment_edit(update, context)

if __name__ == "__main__":
    main()
