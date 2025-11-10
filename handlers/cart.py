from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection
from utils.helpers import format_price_display, convert_eur_to_usd

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.split("_")[3]
    user_id = update.effective_user.id
    
    conn = get_db_connection()
    # Check if product is already in cart
    existing = conn.execute('SELECT * FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id)).fetchone()
    if existing:
        conn.execute('UPDATE cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    else:
        conn.execute('INSERT INTO cart (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
    conn.commit()
    conn.close()
    
    await query.answer("✅ Product added to cart!")

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    conn = get_db_connection()
    cart_items = conn.execute('''SELECT cart.*, products.name, products.price, products.image_id 
                               FROM cart JOIN products ON cart.product_id = products.id 
                               WHERE cart.user_id = ?''', (user_id,)).fetchall()
    conn.close()
    
    if not cart_items:
        keyboard = [
            [InlineKeyboardButton("🛍️ Browse Products", callback_data="view_products")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🛒 Your cart is empty!", reply_markup=reply_markup)
        return
    
    total_eur = 0
    message = "🛒 Your Cart:\n\n"
    
    for item in cart_items:
        item_total_eur = item['price'] * item['quantity']
        total_eur += item_total_eur
        message += f"🛍️ {item['name']}\n"
        message += f" 💰 {format_price_display(item['price'])} × {item['quantity']} = {format_price_display(item_total_eur)}\n\n"
    
    total_usd = convert_eur_to_usd(total_eur)
    message += f"💵 Total: {format_price_display(total_eur)}"
    
    keyboard = [
        [InlineKeyboardButton("💰 Checkout All", callback_data="checkout_cart")],
        [InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")],
        [InlineKeyboardButton("🛍️ Continue Shopping", callback_data="view_products")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    conn = get_db_connection()
    conn.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Browse Products", callback_data="view_products")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🗑️ Cart cleared!", reply_markup=reply_markup)

async def checkout_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    conn = get_db_connection()
    cart_items = conn.execute('''SELECT cart.*, products.name, products.price, products.image_id 
                               FROM cart JOIN products ON cart.product_id = products.id 
                               WHERE cart.user_id = ?''', (user_id,)).fetchall()
    conn.close()
    
    if not cart_items:
        await query.edit_message_text("❌ Cart is empty!")
        return
    
    # Save cart contents
    context.user_data['cart_items'] = [dict(item) for item in cart_items]
    total_eur = sum(item['price'] * item['quantity'] for item in cart_items)
    context.user_data['cart_total'] = total_eur
    
    # Ask for discount code before payment
    from handlers.discount import ask_discount_code
    await ask_discount_code(update, context, from_cart=True)
