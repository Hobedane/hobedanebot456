from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Session, Cart, Product, DiscountCode
from utils.helpers import format_price_eur, format_price_usd
import config

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    with Session() as session:
        cart_items = session.query(Cart).filter_by(user_id=user_id).all()
        products = []
        total_eur = 0
        
        for item in cart_items:
            product = session.query(Product).filter_by(id=item.product_id).first()
            if product:
                products.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price_eur,
                    'quantity': item.quantity
                })
                total_eur += product.price_eur * item.quantity
        
        # Check for discount code
        discount_code = context.user_data.get('discount_code')
        discount_percent = 0
        if discount_code:
            discount = session.query(DiscountCode).filter_by(
                code=discount_code, is_active=True, used=False
            ).first()
            if discount:
                # Check if discount is user-specific
                if discount.user_id and discount.user_id != user_id:
                    discount = None
                elif discount.username and discount.username != update.effective_user.username:
                    discount = None
                else:
                    discount_percent = discount.discount_percent
        
        if discount_percent > 0:
            discount_amount = total_eur * (discount_percent / 100)
            total_eur -= discount_amount
    
    if not products:
        await update.callback_query.edit_message_text(
            "Your cart is empty.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ Browse Products", callback_data="products")]])
        )
        return
    
    text = "🛒 Your Cart:\n\n"
    for product in products:
        text += f"📦 {product['name']}\n"
        text += f"   Quantity: {product['quantity']}\n"
        text += f"   Price: {format_price_eur(product['price'] * product['quantity'])}\n\n"
    
    text += f"💶 Total EUR: {format_price_eur(total_eur)}\n"
    text += f"💵 Total USD: {format_price_usd(total_eur)}\n"
    
    if discount_percent > 0:
        text += f"🎫 Discount: {discount_percent}% applied!\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 Checkout", callback_data="checkout")],
        [InlineKeyboardButton("🎫 Enter Discount Code", callback_data="enter_discount")],
        [InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def enter_discount_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "Please enter your discount code:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="cart")]])
    )
    return 'WAITING_DISCOUNT_CODE'

async def process_discount_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.upper()
    user_id = update.effective_user.id
    
    with Session() as session:
        discount = session.query(DiscountCode).filter_by(
            code=code, is_active=True, used=False
        ).first()
        
        if discount:
            # Check user-specific conditions
            if discount.user_id and discount.user_id != user_id:
                valid = False
            elif discount.username and discount.username != update.effective_user.username:
                valid = False
            else:
                valid = True
        else:
            valid = False
    
    if valid:
        context.user_data['discount_code'] = code
        await update.message.reply_text(
            "✅ Discount code applied!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 View Cart", callback_data="cart")]])
        )
    else:
        await update.message.reply_text(
            "❌ Invalid or expired discount code.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 View Cart", callback_data="cart")]])
        )
    
    return -1

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    with Session() as session:
        session.query(Cart).filter_by(user_id=user_id).delete()
        session.commit()
    
    await update.callback_query.edit_message_text(
        "Cart cleared!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ Browse Products", callback_data="products")]])
    )
