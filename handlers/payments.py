import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_payment_methods, create_order, clear_cart, get_cart, get_exchange_rate
from config import ADMINS

logger = logging.getLogger(__name__)

async def payment_methods(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    payment_methods_list = get_payment_methods()
    enabled_methods = [pm for pm in payment_methods_list if pm['enabled']]
    
    if not enabled_methods:
        await query.edit_message_text("❌ No payment methods are currently available.")
        return
    
    keyboard = []
    for method in enabled_methods:
        keyboard.append([InlineKeyboardButton(
            method['method'].title(),
            callback_data=f"process_payment_{method['method']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='checkout')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("Select payment method:", reply_markup=reply_markup)

async def process_payment(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    payment_method = query.data.replace('process_payment_', '')
    user_id = update.effective_user.id
    
    cart_items = get_cart(user_id)
    if not cart_items:
        await query.edit_message_text("❌ Your cart is empty.")
        return
    
    exchange_rate = get_exchange_rate()
    
    # For simplicity, we'll process the first item in cart
    # In a real scenario, you might want to handle multiple items
    item = cart_items[0]
    total_eur = item['price'] * item['quantity']
    total_usd = total_eur * exchange_rate
    
    # Apply discount if exists
    discount = context.user_data.get('applied_discount')
    if discount:
        discount_amount = total_eur * (discount['percentage'] / 100)
        total_eur -= discount_amount
        total_usd = total_eur * exchange_rate
    
    # Create order
    order_id = create_order(
        user_id=user_id,
        product_id=item['product_id'],
        quantity=item['quantity'],
        amount=total_eur,
        payment_method=payment_method,
        discount_code=discount['code'] if discount else None
    )
    
    # Clear cart
    clear_cart(user_id)
    
    # Show payment instructions based on method
    if payment_method == 'crypto':
        text = (
            f"₿ Crypto Payment\n\n"
            f"Order ID: #{order_id}\n"
            f"Amount: ${total_usd:.2f} USD\n"
            f"Amount: €{total_eur:.2f} EUR\n\n"
            f"Please send the payment to our crypto address:\n"
            f"`1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`\n\n"
            f"After payment, please wait for admin approval."
        )
    elif payment_method == 'bank_transfer':
        text = (
            f"🏦 Bank Transfer\n\n"
            f"Order ID: #{order_id}\n"
            f"Amount: €{total_eur:.2f} EUR\n\n"
            f"Bank Details:\n"
            f"Account: 123456789\n"
            f"Bank: Example Bank\n"
            f"Reference: Order #{order_id}\n\n"
            f"After transfer, please wait for admin approval."
        )
    elif payment_method == 'paypal':
        text = (
            f"💳 PayPal Payment\n\n"
            f"Order ID: #{order_id}\n"
            f"Amount: ${total_usd:.2f} USD\n\n"
            f"Please send payment to: paypal@example.com\n"
            f"Reference: Order #{order_id}\n\n"
            f"After payment, please wait for admin approval."
        )
    else:
        text = f"Payment method {payment_method} not implemented."
    
    # Notify admins about new order
    for admin_id in ADMINS:
        try:
            admin_text = (
                f"🆕 New Order #{order_id}\n\n"
                f"Product: {item['name']}\n"
                f"Quantity: {item['quantity']}\n"
                f"Amount: €{total_eur:.2f}\n"
                f"Payment Method: {payment_method}\n"
                f"User: {update.effective_user.first_name}\n\n"
                f"Approve or reject:"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f'payment_approval_{order_id}_approve'),
                    InlineKeyboardButton("❌ Reject", callback_data=f'payment_approval_{order_id}_reject')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    keyboard = [
        [InlineKeyboardButton("🏠 Back to Start", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)
