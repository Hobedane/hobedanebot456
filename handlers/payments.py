from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import datetime
from database import get_db_connection
from utils.helpers import format_price_display, convert_eur_to_usd
from handlers.discounts import ask_discount_code

async def buy_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.split("_")[2]
    
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    
    context.user_data['selected_product'] = dict(product)
    context.user_data['selected_product_id'] = product_id
    
    # Ask for discount code first
    await ask_discount_code(update, context, from_cart=False)

async def checkout_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    conn = get_db_connection()
    cart_items = conn.execute('''
        SELECT cart.*, products.name, products.price, products.image_id 
        FROM cart 
        JOIN products ON cart.product_id = products.id 
        WHERE cart.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    
    if not cart_items:
        await query.edit_message_text("❌ Cart is empty!")
        return
    
    # Save cart contents
    context.user_data['cart_items'] = [dict(item) for item in cart_items]
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    context.user_data['cart_total'] = total
    
    # Ask for discount code before payment
    await ask_discount_code(update, context, from_cart=True)

async def show_payment_options(update: Update, context: ContextTypes.DEFAULT_TYPE, from_cart=False) -> None:
    query = update.callback_query
    await query.answer()
    
    conn = get_db_connection()
    payments = conn.execute('SELECT * FROM payment_settings').fetchall()
    conn.close()
    
    keyboard = []
    for payment in payments:
        name = {
            'btc': '₿ Bitcoin',
            'eth': 'Ξ Ethereum', 
            'sol': '◎ Solana',
            'ltc': '💎 Litecoin',
            'usdt': '💵 USDT'
        }.get(payment['crypto_type'], payment['crypto_type'].upper())
        keyboard.append([InlineKeyboardButton(name, callback_data=f"payment_{payment['crypto_type']}")])
    
    if from_cart:
        # Use discounted total if available
        total = context.user_data.get('discounted_total') or context.user_data.get('cart_total', 0)
        discount_code = context.user_data.get('discount_code')
        discount_text = f"\n🎫 Discount: {discount_code}" if discount_code else ""
        
        await query.edit_message_text(
            f"💰 Total: {format_price_display(total)}{discount_text}\n\n"
            f"Choose payment method:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        product = context.user_data.get('selected_product', {})
        # Use discounted price if available
        price = context.user_data.get('discounted_price') or product['price']
        discount_code = context.user_data.get('discount_code')
        discount_text = f"\n🎫 Discount: {discount_code}" if discount_code else ""
        
        await query.edit_message_text(
            f"💳 Choose payment method:\n\n"
            f"🛍️ {product['name']}\n"
            f"💰 Price: {format_price_display(price)}{discount_text}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_payment_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    crypto_type = query.data.replace("payment_", "")
    
    # Check if cart or single product
    from_cart = 'cart_items' in context.user_data
    
    if from_cart:
        cart_items = context.user_data['cart_items']
        # Use discounted total if available
        total = context.user_data.get('discounted_total') or context.user_data.get('cart_total', 0)
        products_text = "\n".join([f"• {item['name']} x {item['quantity']}" for item in cart_items])
        message = f"🛍️ Order Contents:\n{products_text}\n💰 Total: {format_price_display(total)}"
    else:
        product = context.user_data.get('selected_product', {})
        # Use discounted price if available
        price = context.user_data.get('discounted_price') or product['price']
        message = f"🛍️ Product: {product['name']}\n💰 Price: {format_price_display(price)}"
    
    # Add discount info if available
    discount_code = context.user_data.get('discount_code')
    if discount_code:
        message += f"\n🎫 Discount Code: {discount_code}"
    
    conn = get_db_connection()
    payment = conn.execute('SELECT * FROM payment_settings WHERE crypto_type = ?', (crypto_type,)).fetchone()
    conn.close()
    
    if not payment:
        await query.edit_message_text("❌ Selected payment method not available!")
        return
    
    # Save payment info
    context.user_data['payment_method'] = crypto_type
    context.user_data['payment_address'] = payment['address']
    
    total_amount = total if from_cart else price
    crypto_amount = total_amount  # In a real scenario, you'd convert to crypto
    
    await query.edit_message_text(
        f"💳 **PAYMENT DETAILS**\n\n"
        f"{message}\n"
        f"⛓️ Blockchain: {payment['blockchain']}\n\n"
        f"📧 **SEND PAYMENT TO ADDRESS:**\n"
        f"`{payment['address']}`\n\n"
        f"💰 **AMOUNT:** {format_price_display(total_amount)}\n\n"
        f"⚠️ **IMPORTANT:**\n"
        f"• Send exactly {total_amount}€ worth of {crypto_type.upper()}\n" 
        f"• Copy address exactly\n\n"
        f"After payment, click the button below:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ PAYMENT MADE", callback_data="confirm_payment")
        ], [
            InlineKeyboardButton("🔙 Back to Payment Methods", callback_data="show_payment_options")
        ]])
    )

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔍 **PAYMENT CONFIRMATION**\n\n"
        "Please enter the payment source address (where you sent from):\n\n"
        "⚠️ **IMPORTANT:** This helps us identify your payment and link it to your order!\n\n"
        "Example: `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="show_payment_options")
        ]])
    )
    context.user_data['waiting_payment_source'] = True
