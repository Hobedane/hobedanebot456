from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection
from utils.helpers import format_price_display

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products WHERE active = 1 AND quantity > 0').fetchall()
    conn.close()
    
    keyboard = []
    for product in products:
        button_text = f"{product['name']} - {format_price_display(product['price'])}"
        if product['quantity'] > 1:
            button_text += f" ({product['quantity']} pcs)"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"product_{product['id']}")])
    
    if not keyboard:
        keyboard.append([InlineKeyboardButton("📦 Products out of stock", callback_data="empty")])
    
    keyboard.append([InlineKeyboardButton("🛒 View Cart", callback_data="view_cart")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🛍️ Our Products:", reply_markup=reply_markup)

async def show_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.split("_")[1]
    
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    
    if not product:
        await query.edit_message_text("❌ Product not found!")
        return
    
    context.user_data['selected_product'] = dict(product)
    context.user_data['selected_product_id'] = product_id
    
    keyboard = [
        [InlineKeyboardButton("💰 Buy Now", callback_data=f"buy_now_{product_id}")],
        [InlineKeyboardButton("🛒 Add to Cart", callback_data=f"add_to_cart_{product_id}")],
        [InlineKeyboardButton("🔙 Back to Products", callback_data="view_products")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    quantity_text = f"📦 Available: {product['quantity']} pcs\n\n" if product['quantity'] > 1 else ""
    message = f"🛍️ {product['name']}\n\n📝 {product['description']}\n💰 Price: {format_price_display(product['price'])}\n{quantity_text}"
    
    # SHOW ONLY TEXT - NO IMAGE (image sent only after payment)
    await query.edit_message_text(message, reply_markup=reply_markup)
