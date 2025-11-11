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

async def handle_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_product_name':
        product_name = update.message.text
        context.user_data['new_product'] = {'name': product_name}
        context.user_data['admin_mode'] = 'adding_product_price'
        await update.message.reply_text(
            f"✅ Name: {product_name}\n\n"
            f"Enter product price (example: 25.00):",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
            ]])
        )

async def handle_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_product_price':
        try:
            price = float(update.message.text)
            context.user_data['new_product']['price'] = price
            context.user_data['admin_mode'] = 'adding_product_description'
            await update.message.reply_text(
                f"✅ Price: {price}€\n\n"
                f"Enter product description:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
                ]])
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid price! Enter a number (example: 25.00):")

async def handle_product_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_product_description':
        description = update.message.text
        context.user_data['new_product']['description'] = description
        context.user_data['admin_mode'] = 'adding_product_quantity'
        await update.message.reply_text(
            f"✅ Description: {description}\n\n"
            f"Enter product quantity (example: 5):",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
            ]])
        )

async def handle_product_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_product_quantity':
        try:
            quantity = int(update.message.text)
            product_data = context.user_data['new_product']
            
            # Save product to database
            conn = get_db_connection()
            conn.execute('''INSERT INTO products (name, price, description, quantity, active) 
                         VALUES (?, ?, ?, ?, ?)''', 
                         (product_data['name'], product_data['price'], product_data['description'], quantity, 1))
            product_id = conn.lastrowid
            conn.commit()
            conn.close()
            
            context.user_data['current_product_id'] = product_id
            context.user_data['admin_mode'] = 'adding_product_image1'
            
            await update.message.reply_text(
                f"✅ Quantity: {quantity}\n\n"
                f"🎉 Product added!\n\n"
                f"Now send the first product image:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
                ]])
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid quantity! Enter a whole number (example: 5):")

# LISA NEED UUED FUNKTSIOONID
async def handle_image2_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_product_image2_choice':
        text = update.message.text.lower()
        if text in ['yes', 'y', 'jah', 'ja']:
            context.user_data['admin_mode'] = 'adding_product_image2'
            await update.message.reply_text(
                "Please send the second product image:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
                ]])
            )
        elif text in ['no', 'n', 'ei']:
            context.user_data['admin_mode'] = 'adding_product_coordinates'
            await update.message.reply_text(
                "No second image added.\n\n"
                "Now you can add map coordinates (optional).\n"
                "Enter coordinates in format:\n"
                "59.4370, 24.7536\n\n"
                "Or send 'skip' to skip.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
                ]])
            )
        else:
            await update.message.reply_text("Please send 'yes' to add second image or 'no' to skip:")

async def handle_product_coordinates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('admin_mode') == 'adding_product_coordinates':
        coordinates = update.message.text
        if coordinates.lower() != 'skip':
            product_id = context.user_data.get('current_product_id')
            conn = get_db_connection()
            conn.execute('UPDATE products SET map_coordinates = ? WHERE id = ?', (coordinates, product_id))
            conn.commit()
            conn.close()
            message = f"📍 Coordinates saved: {coordinates}"
        else:
            message = "📍 No coordinates added."
        
        # Get final product info
        product_id = context.user_data.get('current_product_id')
        conn = get_db_connection()
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        conn.close()
        
        images_count = sum(1 for img in [product['image_id'], product['image_id2']] if img)
        
        await update.message.reply_text(
            f"🎉 Product added completely!\n{message}\n\n"
            f"📦 {product['name']}\n"
            f"💰 {product['price']}€\n"
            f"🖼️ {images_count} image(s) attached\n\n"
            f"Product is now available to clients.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📦 To Product Management", callback_data="admin_products"),
                InlineKeyboardButton("🛠️ To Admin Panel", callback_data="admin_panel")
            ]])
        )
        
        # Reset state
        context.user_data['admin_mode'] = None
        context.user_data['current_product_id'] = None
        context.user_data['new_product'] = None
