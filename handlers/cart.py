import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_cart, clear_cart, get_product, get_exchange_rate
from config import ADMINS

logger = logging.getLogger(__name__)

async def cart(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    cart_items = get_cart(user_id)
    
    if not cart_items:
        keyboard = [
            [InlineKeyboardButton("🛍️ Browse Products", callback_data='products')],
            [InlineKeyboardButton("🔙 Back", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Your cart is empty.", reply_markup=reply_markup)
        return
    
    exchange_rate = get_exchange_rate()
    total_eur = 0
    text = "🛒 Your Cart:\n\n"
    
    # Check stock for each item
    out_of_stock_items = []
    valid_items = []
    
    for item in cart_items:
        product = get_product(item['product_id'])
        if product and product.get('stock', 0) >= item['quantity']:
            item_total = item['price'] * item['quantity']
            total_eur += item_total
            valid_items.append(item)
            
            text += (
                f"🏷️ {item['name']}\n"
                f"💰 €{item['price']:.2f} x {item['quantity']} = €{item_total:.2f}\n"
                f"────────────────────\n"
            )
        else:
            out_of_stock_items.append(item)
    
    # Remove out of stock items from cart
    for item in out_of_stock_items:
        # You might want to implement remove_from_cart function
        pass
    
    total_usd = total_eur * exchange_rate
    
    text += f"\n💰 Total: €{total_eur:.2f} | ${total_usd:.2f}\n"
    
    keyboard = []
    
    if valid_items:
        keyboard.append([InlineKeyboardButton("💰 Checkout", callback_data='checkout')])
    
    keyboard.append([InlineKeyboardButton("🧹 Clear Cart", callback_data='clear_cart')])
    keyboard.append([InlineKeyboardButton("🛍️ Continue Shopping", callback_data='products')])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='start')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if out_of_stock_items:
        text += f"\n⚠️ {len(out_of_stock_items)} item(s) removed due to out of stock."
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def clear_cart_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    clear_cart(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Browse Products", callback_data='products')],
        [InlineKeyboardButton("🔙 Back", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("🧹 Your cart has been cleared.", reply_markup=reply_markup)

async def checkout(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    cart_items = get_cart(user_id)
    
    if not cart_items:
        await query.edit_message_text("Your cart is empty.")
        return
    
    # Check stock for all items
    for item in cart_items:
        product = get_product(item['product_id'])
        if not product or product.get('stock', 0) < item['quantity']:
            await query.edit_message_text(
                f"❌ Sorry, {item['name']} is no longer available in the requested quantity."
            )
            return
    
    exchange_rate = get_exchange_rate()
    total_eur = sum(item['price'] * item['quantity'] for item in cart_items)
    total_usd = total_eur * exchange_rate
    
    text = (
        "💰 Checkout Summary:\n\n"
        f"Total Amount: €{total_eur:.2f} | ${total_usd:.2f}\n\n"
        "Select payment method:"
    )
    
    keyboard = [
        [InlineKeyboardButton("₿ Crypto", callback_data='process_payment_crypto')],
        [InlineKeyboardButton("🏦 Bank Transfer", callback_data='process_payment_bank_transfer')],
        [InlineKeyboardButton("💳 PayPal", callback_data='process_payment_paypal')],
        [InlineKeyboardButton("🔙 Back to Cart", callback_data='cart')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)
