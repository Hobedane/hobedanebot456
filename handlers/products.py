from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Session, Product, Cart
from utils.helpers import format_price_eur, get_message

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session() as session:
        products = session.query(Product).filter_by(is_active=True).all()
    
    if not products:
        await update.callback_query.edit_message_text(
            "No products available at the moment.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
        )
        return

    keyboard = []
    for product in products:
        keyboard.append([InlineKeyboardButton(
            f"{product.name} - {format_price_eur(product.price_eur)}",
            callback_data=f"view_product_{product.id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    
    await update.callback_query.edit_message_text(
        "🛍️ Available Products:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def view_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_id = int(update.callback_query.data.split('_')[-1])
    
    with Session() as session:
        product = session.query(Product).filter_by(id=product_id).first()
    
    if not product:
        await update.callback_query.edit_message_text("Product not found.")
        return

    text = f"""
📦 {product.name}
💶 Price: {format_price_eur(product.price_eur)}
📝 Description: {product.description or 'No description'}
🔄 Available: {product.quantity}
    """
    
    keyboard = [
        [InlineKeyboardButton("🛒 Add to Cart", callback_data=f"add_cart_{product.id}")],
        [InlineKeyboardButton("🔙 Back to Products", callback_data="products")]
    ]
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_id = int(update.callback_query.data.split('_')[-1])
    user_id = update.effective_user.id
    
    with Session() as session:
        # Check if already in cart
        existing = session.query(Cart).filter_by(user_id=user_id, product_id=product_id).first()
        if existing:
            existing.quantity += 1
        else:
            cart_item = Cart(user_id=user_id, product_id=product_id)
            session.add(cart_item)
        session.commit()
    
    added_message = get_message('added_to_cart')
    await update.callback_query.answer(added_message, show_alert=True)
