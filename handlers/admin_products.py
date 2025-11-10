from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection
from utils.helpers import is_admin
from config import logger

async def admin_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id').fetchall()
    conn.close()
    
    keyboard = []
    for product in products:
        status = "✅" if product['active'] else "❌"
        button_text = f"{status} {product['name']} - {product['price']}€"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"admin_edit_product_{product['id']}")])
    
    keyboard.extend([
        [InlineKeyboardButton("➕ Add New Product", callback_data="admin_add_product")],
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "📦 Product Management:\n\n"
        "Click on product to edit its settings:",
        reply_markup=reply_markup
    )

async def admin_edit_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("admin_edit_product_", "")
    
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    
    if not product:
        await query.edit_message_text("❌ Product not found!")
        return
    
    status = "✅ Active" if product['active'] else "❌ Inactive"
    images_info = f"🖼️ Images: {1 if product['image_id'] else 0}{' + 1' if product['image_id2'] else ''}"
    message = (
        f"📦 Product: {product['name']}\n"
        f"💰 Price: {product['price']}€\n"
        f"📝 Description: {product['description']}\n"
        f"📦 Quantity: {product['quantity']}\n"
        f"📍 Coordinates: {product['map_coordinates'] or 'Not set'}\n"
        f"🎯 Status: {status}\n"
        f"{images_info}"
    )
    
    keyboard = [
        [InlineKeyboardButton("✏️ Edit Name", callback_data=f"edit_name_{product_id}")],
        [InlineKeyboardButton("💰 Edit Price", callback_data=f"edit_price_{product_id}")],
        [InlineKeyboardButton("📝 Edit Description", callback_data=f"edit_desc_{product_id}")],
        [InlineKeyboardButton("📦 Edit Quantity", callback_data=f"edit_quantity_{product_id}")],
        [InlineKeyboardButton("📍 Edit Coordinates", callback_data=f"edit_coords_{product_id}")],
        [InlineKeyboardButton("🖼️ Add/Replace Image 1", callback_data=f"edit_image1_{product_id}")],
        [InlineKeyboardButton("🖼️ Add/Replace Image 2", callback_data=f"edit_image2_{product_id}")],
        [InlineKeyboardButton("🔄 Toggle Active", callback_data=f"toggle_active_{product_id}")],
        [InlineKeyboardButton("🗑️ Delete Product", callback_data=f"delete_product_{product_id}")],
        [InlineKeyboardButton("🔙 Back to Products", callback_data="admin_products")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)

async def admin_add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("❌ No access!")
        return
        
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Enter product name:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
        ]])
    )
    context.user_data['admin_mode'] = 'adding_product_name'
