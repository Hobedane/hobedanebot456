from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection
from utils.helpers import is_admin
from config import logger

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    
    conn = get_db_connection()
    # Product statistics
    products_count = conn.execute('SELECT COUNT() FROM products').fetchone()[0]
    active_products = conn.execute('SELECT COUNT() FROM products WHERE active = 1 AND quantity > 0').fetchone()[0]
    
    # Order statistics
    total_orders = conn.execute('SELECT COUNT() FROM orders').fetchone()[0]
    completed_orders = conn.execute('SELECT COUNT() FROM orders WHERE status = "completed"').fetchone()[0]
    pending_orders = conn.execute('SELECT COUNT() FROM orders WHERE status = "pending"').fetchone()[0]
    
    # Discount code statistics
    total_codes = conn.execute('SELECT COUNT() FROM discount_codes').fetchone()[0]
    active_codes = conn.execute('SELECT COUNT() FROM discount_codes WHERE active = 1').fetchone()[0]
    
    # Cart statistics
    cart_items = conn.execute('SELECT COUNT(*) FROM cart').fetchone()[0]
    conn.close()
    
    message = (
        f"📊 STORE STATISTICS\n\n"
        f"🛍️ PRODUCTS:\n"
        f"• All products: {products_count}\n"
        f"• Active products: {active_products}\n\n"
        f"📦 ORDERS:\n"
        f"• All orders: {total_orders}\n"
        f"• Completed: {completed_orders}\n"
        f"• Pending: {pending_orders}\n\n"
        f"🛒 CARTS:\n"
        f"• Products in carts: {cart_items}\n\n"
        f"🎫 DISCOUNT CODES:\n"
        f"• All codes: {total_codes}\n"
        f"• Active: {active_codes}"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)
