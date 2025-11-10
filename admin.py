from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Session, Product, CryptoAddress, Order, Statistics
from utils.helpers import get_admin_keyboard, format_price_eur, get_message
import config

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in config.ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!", show_alert=True)
        return
    
    await update.callback_query.edit_message_text(
        "👑 Admin Panel",
        reply_markup=get_admin_keyboard()
    )

async def admin_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Add Product", callback_data="add_product")],
        [InlineKeyboardButton("📋 List Products", callback_data="list_products")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]
    ]
    
    await update.callback_query.edit_message_text(
        "📦 Product Management:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session() as session:
        addresses = session.query(CryptoAddress).all()
    
    keyboard = []
    for addr in addresses:
        status = "✅" if addr.is_active else "❌"
        keyboard.append([InlineKeyboardButton(
            f"{status} {addr.currency}",
            callback_data=f"edit_crypto_{addr.id}"
        )])
    
    keyboard.append([InlineKeyboardButton("➕ Add Address", callback_data="add_crypto")])
    keyboard.append([InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")])
    
    text = "💰 Crypto Address Management\n\nClick on an address to edit it."
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session() as session:
        stats = session.query(Statistics).first()
        products_count = session.query(Product).count()
        pending_orders = session.query(Order).filter_by(status='pending').count()
        completed_orders = session.query(Order).filter_by(status='confirmed').count()
    
    if not stats:
        stats = Statistics()
    
    text = f"""
📊 Shop Statistics

👥 Total Visits: {stats.visits}
📦 Total Products: {products_count}
💰 Total Revenue: {format_price_eur(stats.revenue_eur)}
📋 Total Orders: {stats.orders_count}
⏳ Pending Payments: {pending_orders}
✅ Completed Orders: {completed_orders}
    """
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]])
    )

async def admin_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session() as session:
        pending_orders = session.query(Order).filter_by(status='pending').all()
    
    if not pending_orders:
        await update.callback_query.edit_message_text(
            "No pending payments.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]])
        )
        return
    
    text = "💳 Pending Payments:\n\n"
    
    for order in pending_orders:
        text += f"Order #{order.id}\n"
        text += f"User: {order.user_id}\n"
        text += f"Amount: {format_price_eur(order.total_eur)}\n"
        text += f"Currency: {order.currency}\n"
        text += f"Source: `{order.source_address}`\n"
        text += f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        text += "─" * 20 + "\n"
    
    keyboard = []
    for order in pending_orders:
        keyboard.append([InlineKeyboardButton(
            f"✅ Confirm Order #{order.id}",
            callback_data=f"confirm_order_{order.id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")])
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = int(update.callback_query.data.split('_')[-1])
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Confirm", callback_data=f"final_confirm_{order_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_confirm_{order_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_payments")]
    ]
    
    await update.callback_query.edit_message_text(
        "⚠️ Are you sure you want to confirm this payment?\n\n"
        "This will send the product images to the customer.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def final_confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = int(update.callback_query.data.split('_')[-1])
    
    with Session() as session:
        order = session.query(Order).filter_by(id=order_id).first()
        if not order:
            await update.callback_query.edit_message_text("Order not found.")
            return
        
        # Get products
        products = session.query(Product).filter(Product.id.in_(order.products)).all()
        
        # Update order status
        order.status = 'confirmed'
        
        # Update statistics
        stats = session.query(Statistics).first()
        if not stats:
            stats = Statistics()
            session.add(stats)
        stats.orders_count += 1
        stats.revenue_eur += order.total_eur
        
        session.commit()
    
    # Send product images to customer
    from main import application
    try:
        for product in products:
            if product.image1:
                await application.bot.send_photo(
                    order.user_id,
                    product.image1,
                    caption=f"📦 {product.name}\n{product.description or ''}"
                )
            if product.image2:
                await application.bot.send_photo(
                    order.user_id,
                    product.image2,
                    caption=f"📦 {product.name} - Additional Image"
                )
        
        # Send success message
        success_message = get_message('success_payment')
        await application.bot.send_message(
            order.user_id,
            success_message
        )
        
    except Exception as e:
        print(f"Failed to send products to user {order.user_id}: {e}")
        # Notify admin about the error
        await update.callback_query.edit_message_text(
            f"✅ Order confirmed but failed to send some products to user. Error: {e}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]])
        )
        return
    
    await update.callback_query.edit_message_text(
        f"✅ Order #{order_id} confirmed! Products sent to customer.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]])
    )