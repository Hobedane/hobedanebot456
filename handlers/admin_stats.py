import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_admin_stats, get_products, get_discounts

logger = logging.getLogger(__name__)

async def admin_stats(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    stats = get_admin_stats()
    products = get_products()
    discounts = get_discounts()
    
    # Calculate additional stats
    total_products_value = sum(product['price'] for product in products)
    active_discounts = [d for d in discounts if d['active']]
    
    text = (
        "📊 Detailed Statistics:\n\n"
        f"👥 Total Users: {stats.get('total_users', 0)}\n"
        f"📦 Total Orders: {stats.get('total_orders', 0)}\n"
        f"💰 Total Revenue: €{stats.get('total_revenue', 0):.2f}\n"
        f"🛍️ Active Products: {stats.get('active_products', 0)}\n"
        f"🏪 Total Products Value: €{total_products_value:.2f}\n"
        f"🎫 Active Discounts: {stats.get('active_discounts', 0)}\n"
        f"📋 Total Discount Codes: {len(discounts)}\n"
    )
    
    # Add product list
    if products:
        text += "\n📦 Products:\n"
        for product in products[:10]:  # Show first 10 products
            status = "✅" if product['active'] else "❌"
            stock_status = f"Stock: {product.get('stock', 0)}"
            text += f"{status} {product['name']} - €{product['price']:.2f} ({stock_status})\n"
        
        if len(products) > 10:
            text += f"... and {len(products) - 10} more products\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data='admin_stats')],
        [InlineKeyboardButton("🔙 Back", callback_data='admin')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)
