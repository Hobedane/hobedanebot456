import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection, get_exchange_rate
from utils.helpers import format_price_display, convert_eur_to_usd
from config import ADMIN_USER_ID, logger

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
        total_eur = context.user_data.get('discounted_total') or context.user_data.get('cart_total', 0)
        discount_code = context.user_data.get('discount_code')
        discount_text = f"\n🎫 Discount: {discount_code}" if discount_code else ""
        
        await query.edit_message_text(
            f"💰 Total: {format_price_display(total_eur)}{discount_text}\n\n"
            f"Choose payment method:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        product = context.user_data.get('selected_product', {})
        # Use discounted price if available
        price_eur = context.user_data.get('discounted_price') or product['price']
        discount_code = context.user_data.get('discount_code')
        discount_text = f"\n🎫 Discount: {discount_code}" if discount_code else ""
        
        await query.edit_message_text(
            f"💳 Choose payment method:\n\n"
            f"🛍️ {product['name']}\n"
            f"💰 Price: {format_price_display(price_eur)}{discount_text}",
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
        total_eur = context.user_data.get('discounted_total') or context.user_data.get('cart_total', 0)
        products_text = "\n".join([f"• {item['name']} x {item['quantity']}" for item in cart_items])
        message = f"🛍️ Order Contents:\n{products_text}\n💰 Total: {format_price_display(total_eur)}"
    else:
        product = context.user_data.get('selected_product', {})
        # Use discounted price if available
        price_eur = context.user_data.get('discounted_price') or product['price']
        message = f"🛍️ Product: {product['name']}\n💰 Price: {format_price_display(price_eur)}"
    
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
    
    total_amount = total_eur if from_cart else price_eur
    
    await query.edit_message_text(
        f"💳 PAYMENT DETAILS\n\n"
        f"{message}\n"
        f"⛓️ Blockchain: {payment['blockchain']}\n\n"
        f"📧 SEND PAYMENT TO ADDRESS:\n"
        f"{payment['address']}\n\n"
        f"⚠️ IMPORTANT:\n"
        f"• Send exactly {format_price_display(total_amount)} worth of {crypto_type.upper()}\n"
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
        "🔍 PAYMENT CONFIRMATION\n\n"
        "Please enter the payment source address (where you sent from):\n\n"
        "⚠️ IMPORTANT: This helps us identify your payment and link it to your order!\n\n"
        "Example: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="show_payment_options")
        ]])
    )
    context.user_data['waiting_payment_source'] = True

async def handle_payment_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('waiting_payment_source'):
        payment_source = update.message.text
        # Save payment source address
        context.user_data['payment_source'] = payment_source
        context.user_data['waiting_payment_source'] = False
        
        # Continue with payment confirmation
        await process_payment_confirmation(update, context)

async def process_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    payment_source = context.user_data.get('payment_source', 'Not specified')
    discount_code = context.user_data.get('discount_code')
    
    # Check if cart or single product
    from_cart = 'cart_items' in context.user_data
    
    if from_cart:
        # Cart payment
        cart_items = context.user_data['cart_items']
        # Use discounted total if available
        total_eur = context.user_data.get('discounted_total') or context.user_data.get('cart_total', 0)
        
        # Create orders for each product
        order_ids = []
        for item in cart_items:
            order_id = f"ORD{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{item['id']}"
            order_ids.append(order_id)
            
            conn = get_db_connection()
            conn.execute('''INSERT INTO orders (order_id, client_id, product_id, status, final_price, payment_source_address, discount_code) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                         (order_id, user.id, item['id'], 'pending', total_eur, payment_source, discount_code))
            conn.commit()
            conn.close()
        
        # Clear cart
        conn = get_db_connection()
        conn.execute('DELETE FROM cart WHERE user_id = ?', (user.id,))
        conn.commit()
        conn.close()
        
        order_id_text = ", ".join(order_ids)
        discount_text = f"\n🎫 Discount Code: {discount_code}" if discount_code else ""
        
        await update.message.reply_text(
            f"✅ Notified admin of your payment!\n"
            f"🆔 Order IDs: {order_id_text}\n"
            f"💰 Total: {format_price_display(total_eur)}{discount_text}\n"
            f"📧 Payment source address: {payment_source}\n\n"
            f"Admin will check your transaction and send products after confirmation."
        )
        
        # SEND MESSAGE TO ADMIN
        user_info = f"{user.first_name} {user.last_name or ''} (@{user.username or 'none'})"
        products_text = "\n".join([f"• {item['name']} x {item['quantity']}" for item in cart_items])
        admin_message = (
            f"🔄 CART PAYMENT AWAITING CONFIRMATION!\n\n"
            f"👤 Client: {user_info}\n"
            f"🆔 User ID: {user.id}\n"
            f"🛍️ Products:\n{products_text}\n"
            f"💰 Total: {format_price_display(total_eur)}\n"
            f"🆔 Order IDs: {order_id_text}\n"
            f"⛓️ Crypto: {context.user_data.get('payment_method', '').upper()}\n"
            f"📧 Payment source address: {payment_source}\n"
        )
        if discount_code:
            admin_message += f"🎫 Discount Code: {discount_code}\n"
        admin_message += f"⏰ Time: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        admin_message += f"Is payment visible in your wallet?"
        
    else:
        # Single product payment
        product = context.user_data.get('selected_product', {})
        # Use discounted price if available
        price_eur = context.user_data.get('discounted_price') or product['price']
        discount_code = context.user_data.get('discount_code')
        
        # Create order ID
        order_id = f"ORD{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Save order
        conn = get_db_connection()
        conn.execute('''INSERT INTO orders (order_id, client_id, product_id, status, final_price, payment_source_address, discount_code) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                     (order_id, user.id, product['id'], 'pending', price_eur, payment_source, discount_code))
        conn.commit()
        conn.close()
        
        discount_text = f"\n🎫 Discount Code: {discount_code}" if discount_code else ""
        
        await update.message.reply_text(
            f"✅ Notified admin of your payment!\n"
            f"🆔 Your Order ID: {order_id}\n"
            f"💰 Price: {format_price_display(price_eur)}{discount_text}\n"
            f"📧 Payment source address: {payment_source}\n\n"
            f"Admin will check your transaction and send product after confirmation."
        )
        
        # SEND MESSAGE TO ADMIN
        user_info = f"{user.first_name} {user.last_name or ''} (@{user.username or 'none'})"
        admin_message = (
            f"🔄 PAYMENT AWAITING CONFIRMATION!\n\n"
            f"👤 Client: {user_info}\n"
            f"🆔 User ID: {user.id}\n"
            f"🛍️ Product: {product['name']}\n"
            f"💰 Price: {format_price_display(price_eur)}\n"
            f"🆔 Order ID: {order_id}\n"
            f"⛓️ Crypto: {context.user_data.get('payment_method', '').upper()}\n"
            f"📧 Payment source address: {payment_source}\n"
        )
        if discount_code:
            admin_message += f"🎫 Discount Code: {discount_code}\n"
        admin_message += f"⏰ Time: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        admin_message += f"Is payment visible in your wallet?"
    
    admin_keyboard = [
        [
            InlineKeyboardButton("✅ Confirm Payment", callback_data=f"approve_{order_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{order_id}")
        ]
    ]
    admin_reply_markup = InlineKeyboardMarkup(admin_keyboard)
    
    await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=admin_message,
        reply_markup=admin_reply_markup
    )
    
    # Clear user data
    context.user_data.clear()

# Payment approval functions would continue here...
