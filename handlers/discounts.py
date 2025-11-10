from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection
from utils.helpers import format_price_display, convert_eur_to_usd

async def ask_discount_code(update: Update, context: ContextTypes.DEFAULT_TYPE, from_cart=False) -> None:
    query = update.callback_query
    await query.answer()
    
    if from_cart:
        total_eur = context.user_data.get('cart_total', 0)
        message = f"💰 Cart Total: {format_price_display(total_eur)}\n\n"
    else:
        product = context.user_data.get('selected_product', {})
        message = f"🛍️ {product['name']}\n💰 Price: {format_price_display(product['price'])}\n\n"
    
    message += "Do you have a discount code? Enter it below or press 'No Code' to continue:"
    
    keyboard = [
        [InlineKeyboardButton("🚫 No Code", callback_data="no_discount_code")],
        [InlineKeyboardButton("🔙 Back", callback_data="view_cart" if from_cart else f"product_{context.user_data['selected_product_id']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)
    context.user_data['waiting_discount_code'] = True
    context.user_data['discount_from_cart'] = from_cart

async def handle_discount_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kliendi poolne discount code sisestus"""
    if context.user_data.get('waiting_discount_code'):
        discount_code = update.message.text.upper()
        from_cart = context.user_data.get('discount_from_cart', False)
        
        conn = get_db_connection()
        code_data = conn.execute('''SELECT * FROM discount_codes 
                                  WHERE code = ? AND active = 1 
                                  AND (expires IS NULL OR expires > DATE('now')) 
                                  AND (max_uses = -1 OR used_count < max_uses)''', 
                                  (discount_code,)).fetchone()
        conn.close()
        
        if code_data:
            # Valid discount code
            discount_percent = code_data['discount_percent']
            
            if from_cart:
                original_total_eur = context.user_data.get('cart_total', 0)
                discount_amount_eur = original_total_eur * (discount_percent / 100)
                discounted_total_eur = original_total_eur - discount_amount_eur
                
                context.user_data['discounted_total'] = discounted_total_eur
                context.user_data['discount_code'] = discount_code
                
                message = (f"🎫 Discount Applied!\n"
                         f"💰 Original: {format_price_display(original_total_eur)}\n"
                         f"📊 Discount: {discount_percent}%\n"
                         f"💵 New Total: {format_price_display(discounted_total_eur)}")
            else:
                product = context.user_data.get('selected_product', {})
                original_price_eur = product['price']
                discount_amount_eur = original_price_eur * (discount_percent / 100)
                discounted_price_eur = original_price_eur - discount_amount_eur
                
                context.user_data['discounted_price'] = discounted_price_eur
                context.user_data['discount_code'] = discount_code
                
                message = (f"🎫 Discount Applied!\n"
                         f"💰 Original: {format_price_display(original_price_eur)}\n"
                         f"📊 Discount: {discount_percent}%\n"
                         f"💵 New Price: {format_price_display(discounted_price_eur)}")
            
            keyboard = [[InlineKeyboardButton("✅ Continue to Payment", callback_data="proceed_to_payment")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(message, reply_markup=reply_markup)
        else:
            # Invalid discount code
            await update.message.reply_text("❌ Invalid or expired discount code. Please try again or press 'No Code':")
            return
        
        context.user_data['waiting_discount_code'] = False

async def no_discount_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    context.user_data['waiting_discount_code'] = False
    context.user_data['discount_code'] = None
    from_cart = context.user_data.get('discount_from_cart', False)
    
    from handlers.payment import show_payment_options
    await show_payment_options(update, context, from_cart=from_cart)

async def proceed_to_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    from_cart = context.user_data.get('discount_from_cart', False)
    from handlers.payment import show_payment_options
    await show_payment_options(update, context, from_cart=from_cart)
