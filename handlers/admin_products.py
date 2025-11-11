import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_products, get_product, add_to_cart
from config import ADMINS

logger = logging.getLogger(__name__)

async def products(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    # Get products - AINULT need, millel on stock > 0
    products_list = get_products(in_stock_only=True)
    
    if not products_list:
        keyboard = [[InlineKeyboardButton("Back", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("No products available at the moment.", reply_markup=reply_markup)
        return
    
    # Create product buttons (2 per row)
    keyboard = []
    row = []
    for product in products_list:
        button = InlineKeyboardButton(
            f"{product['name']} - €{product['price']:.2f}",
            callback_data=f"view_product_{product['id']}"
        )
        row.append(button)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("Back", callback_data='start')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("Available Products:", reply_markup=reply_markup)

async def view_product(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split('_')[-1])
    product = get_product(product_id)
    
    if not product:
        await query.edit_message_text("Product not found.")
        return
    
    # Check if product is in stock
    if product.get('stock', 0) <= 0:
        keyboard = [[InlineKeyboardButton("Back to Products", callback_data='products')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"❌ {product['name']} is out of stock.\n\n"
            f"Please check back later.",
            reply_markup=reply_markup
        )
        return
    
    text = (
        f"🏷️ {product['name']}\n\n"
        f"📝 {product['description']}\n\n"
        f"💰 Price: €{product['price']:.2f}\n"
        f"📦 In stock: {product.get('stock', 1)}\n"
    )
    
    # EI KUVA KOORDINAATE EGA PILTE ENNE OSTU!
    
    keyboard = [
        [InlineKeyboardButton("🛒 Add to Cart", callback_data=f"add_to_cart_{product['id']}")],
        [InlineKeyboardButton("Back to Products", callback_data='products')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # EI SAADA PILTI - AINULT TEKST
    await query.edit_message_text(text, reply_markup=reply_markup)

async def add_to_cart_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split('_')[-1])
    user_id = update.effective_user.id
    
    # Check if product is still in stock
    product = get_product(product_id)
    if not product or product.get('stock', 0) <= 0:
        await query.edit_message_text("❌ Sorry, this product is out of stock.")
        return
    
    add_to_cart(user_id, product_id)
    
    keyboard = [
        [InlineKeyboardButton("🛒 View Cart", callback_data='cart')],
        [InlineKeyboardButton("🛍️ Continue Shopping", callback_data='products')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ {product['name']} added to cart!",
        reply_markup=reply_markup
    )
