from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Session, CryptoAddress, Order, Cart, Product, Statistics, DiscountCode
from utils.helpers import get_message, format_price_eur, format_price_usd
import config

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    with Session() as session:
        # Calculate total
        cart_items = session.query(Cart).filter_by(user_id=user_id).all()
        total_eur = 0
        product_ids = []
        
        for item in cart_items:
            product = session.query(Product).filter_by(id=item.product_id).first()
            if product:
                total_eur += product.price_eur * item.quantity
                product_ids.append(product.id)
        
        # Apply discount
        discount_code = context.user_data.get('discount_code')
        discount_percent = 0
        if discount_code:
            discount = session.query(DiscountCode).filter_by(code=discount_code).first()
            if discount:
                discount_percent = discount.discount_percent
        
        if discount_percent > 0:
            total_eur = total_eur * (1 - discount_percent / 100)
        
        total_usd = total_eur * config.EXCHANGE_RATE
        
        # Get crypto addresses
        crypto_addresses = session.query(CryptoAddress).filter_by(is_active=True).all()
    
    if not crypto_addresses:
        await update.callback_query.edit_message_text(
            "No payment methods available. Please contact admin.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="cart")]])
        )
        return
    
    keyboard = []
    for crypto in crypto_addresses:
        keyboard.append([InlineKeyboardButton(
            crypto.currency,
            callback_data=f"select_crypto_{crypto.id}_{total_eur:.2f}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="cart")])
    
    text = f"💰 Checkout\n\n"
    text += f"💶 Total: {format_price_eur(total_eur)}\n"
    text += f"💵 Total: {format_price_usd(total_eur)}\n\n"
    text += "Select payment method:"
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def select_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_parts = update.callback_query.data.split('_')
    crypto_id = int(data_parts[2])
    total_eur = float(data_parts[3])
    
    with Session() as session:
        crypto = session.query(CryptoAddress).filter_by(id=crypto_id).first()
        total_usd = total_eur * config.EXCHANGE_RATE
    
    if not crypto:
        await update.callback_query.edit_message_text("Payment method not found.")
        return
    
    payment_instructions = get_message('payment_instructions').format(
        amount=total_eur,
        currency=crypto.currency,
        address=crypto.address
    )
    
    text = f"💰 Payment Instructions\n\n{payment_instructions}\n\n"
    text += f"💶 Amount EUR: {format_price_eur(total_eur)}\n"
    text += f"💵 Amount USD: {format_price_usd(total_eur)}"
    
    keyboard = [
        [InlineKeyboardButton("✅ I Have Paid", callback_data=f"confirm_payment_{crypto_id}_{total_eur:.2f}")],
        [InlineKeyboardButton("🔙 Back", callback_data="checkout")]
    ]
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_parts = update.callback_query.data.split('_')
    crypto_id = int(data_parts[2])
    total_eur = float(data_parts[3])
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, I have paid", callback_data=f"enter_source_{crypto_id}_{total_eur:.2f}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"select_crypto_{crypto_id}_{total_eur:.2f}")]
    ]
    
    await update.callback_query.edit_message_text(
        "⚠️ Are you sure you have made the payment?\n\n"
        "Please confirm only after you have sent the cryptocurrency.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def enter_source_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_parts = update.callback_query.data.split('_')
    crypto_id = int(data_parts[2])
    total_eur = float(data_parts[3])
    
    context.user_data['pending_payment'] = {
        'crypto_id': crypto_id,
        'total_eur': total_eur
    }
    
    await update.callback_query.edit_message_text(
        "Please enter the source address (the address you sent the payment FROM):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="cart")]])
    )
    return 'WAITING_SOURCE_ADDRESS'

async def process_source_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    source_address = update.message.text
    user_id = update.effective_user.id
    payment_data = context.user_data.get('pending_payment')
    
    if not payment_data:
        await update.message.reply_text("Payment session expired. Please start over.")
        return -1
    
    with Session() as session:
        # Get cart items
        cart_items = session.query(Cart).filter_by(user_id=user_id).all()
        product_ids = [item.product_id for item in cart_items]
        
        # Create order
        crypto = session.query(CryptoAddress).filter_by(id=payment_data['crypto_id']).first()
        order = Order(
            user_id=user_id,
            total_eur=payment_data['total_eur'],
            total_usd=payment_data['total_eur'] * config.EXCHANGE_RATE,
            currency=crypto.currency,
            crypto_address=crypto.address,
            source_address=source_address,
            products=product_ids,
            status='pending'
        )
        session.add(order)
        
        # Clear cart
        session.query(Cart).filter_by(user_id=user_id).delete()
        
        # Mark discount code as used if applicable
        discount_code = context.user_data.get('discount_code')
        if discount_code:
            discount = session.query(DiscountCode).filter_by(code=discount_code).first()
            if discount:
                discount.used = True
        
        session.commit()
        order_id = order.id
    
    # Notify admin
    from main import application
    for admin_id in config.ADMIN_IDS:
        try:
            await application.bot.send_message(
                admin_id,
                f"🆕 New Payment Pending!\n\n"
                f"Order ID: #{order_id}\n"
                f"User: @{update.effective_user.username or 'N/A'} ({user_id})\n"
                f"Amount: {format_price_eur(payment_data['total_eur'])}\n"
                f"Currency: {crypto.currency}\n"
                f"Source Address: `{source_address}`\n\n"
                f"Check your wallet and confirm payment.",
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")
    
    await update.message.reply_text(
        "✅ Payment registered! Admin will verify your payment and send your products soon.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ Continue Shopping", callback_data="products")]])
    )
    
    # Clear temporary data
    if 'pending_payment' in context.user_data:
        del context.user_data['pending_payment']
    if 'discount_code' in context.user_data:
        del context.user_data['discount_code']
    
    return -1
