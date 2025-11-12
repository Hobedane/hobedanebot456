from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from database import get_db_connection
from utils.helpers import format_price_display

logger = logging.getLogger(__name__)

async def admin_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id').fetchall()
    conn.close()
    
    keyboard = []
    for product in products:
        status = "✅" if product['active'] else "❌"
        button_text = f"{status} {product['name']} - {format_price_display(product['price'])}"
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
        f"💰 Price: {format_price_display(product['price'])}\n"
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

async def edit_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("edit_name_", "")
    
    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'name'
    
    await query.edit_message_text(
        "Enter new product name:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data=f"admin_edit_product_{product_id}")
        ]])
    )

async def edit_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("edit_price_", "")
    
    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'price'
    
    await query.edit_message_text(
        "Enter new product price (example: 25.00):",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data=f"admin_edit_product_{product_id}")
        ]])
    )

async def edit_product_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("edit_desc_", "")
    
    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'description'
    
    await query.edit_message_text(
        "Enter new product description:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data=f"admin_edit_product_{product_id}")
        ]])
    )

async def edit_product_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("edit_quantity_", "")
    
    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'quantity'
    
    await query.edit_message_text(
        "Enter new product quantity:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data=f"admin_edit_product_{product_id}")
        ]])
    )

async def edit_product_coordinates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("edit_coords_", "")
    
    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'coordinates'
    
    await query.edit_message_text(
        "Enter new map coordinates (or 'none' to remove):",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data=f"admin_edit_product_{product_id}")
        ]])
    )

async def edit_product_image1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("edit_image1_", "")
    
    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'image1'
    
    await query.edit_message_text(
        "Send new image for product (first image):",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data=f"admin_edit_product_{product_id}")
        ]])
    )

async def edit_product_image2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("edit_image2_", "")
    
    context.user_data['editing_product_id'] = product_id
    context.user_data['editing_field'] = 'image2'
    
    await query.edit_message_text(
        "Send new image for product (second image):",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data=f"admin_edit_product_{product_id}")
        ]])
    )

async def toggle_product_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("toggle_active_", "")
    
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    new_status = 0 if product['active'] else 1
    conn.execute('UPDATE products SET active = ? WHERE id = ?', (new_status, product_id))
    conn.commit()
    conn.close()
    
    status_text = "activated" if new_status else "deactivated"
    await query.answer(f"Product {status_text}!")
    await admin_edit_product(update, context)

async def delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("delete_product_", "")
    
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    
    if not product:
        await query.edit_message_text("❌ Product not found!")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("✅ YES, delete", callback_data=f"confirm_delete_{product_id}"),
            InlineKeyboardButton("❌ NO, cancel", callback_data=f"admin_edit_product_{product_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🗑️ **DELETE CONFIRMATION**\n\n"
        f"Are you sure you want to delete this product?\n\n"
        f"📦 {product['name']}\n"
        f"💰 {format_price_display(product['price'])}\n\n"
        f"⚠️ **This action cannot be undone!**",
        reply_markup=reply_markup
    )

async def confirm_delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    product_id = query.data.replace("confirm_delete_", "")
    
    conn = get_db_connection()
    # Get product name for confirmation message
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    # Delete the product
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    
    await query.edit_message_text(
        f"🗑️ Product deleted!\n\n"
        f"📦 {product['name']}\n"
        f"💰 {format_price_display(product['price'])}\n\n"
        f"Product has been permanently removed from the database."
    )

async def admin_add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
                f"✅ Price: {format_price_display(price)}\n\n"
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
        
        # MUUDATUS: Salvesta toode kohe andmebaasi quantity=1-ga
        product_data = context.user_data['new_product']
        
        conn = get_db_connection()
        conn.execute('''INSERT INTO products (name, price, description, quantity, active) 
                      VALUES (?, ?, ?, ?, ?)''', 
                    (product_data['name'], product_data['price'], product_data['description'], 1, 1))
        product_id = conn.lastrowid
        conn.commit()
        conn.close()
        
        context.user_data['current_product_id'] = product_id
        context.user_data['admin_mode'] = 'adding_product_image1'
        
        await update.message.reply_text(
            f"✅ Description: {description}\n\n"
            f"🎉 Product added to database with quantity 1!\n\n"
            f"Now send the first product image:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
            ]])
        )

async def handle_product_image1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Esimese pildi lisamine tootele"""
    if context.user_data.get('admin_mode') == 'adding_product_image1' and update.message.photo:
        product_id = context.user_data.get('current_product_id')
        photo_id = update.message.photo[-1].file_id
        
        conn = get_db_connection()
        conn.execute('UPDATE products SET image_id = ? WHERE id = ?', (photo_id, product_id))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            "✅ First image saved!\n\n"
            "Would you like to add a second image?\n"
            "Send 'yes' to add second image or 'no' to skip:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
            ]])
        )
        context.user_data['admin_mode'] = 'adding_product_image2_choice'

async def handle_product_image2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Teise pildi lisamine tootele"""
    if context.user_data.get('admin_mode') == 'adding_product_image2' and update.message.photo:
        product_id = context.user_data.get('current_product_id')
        photo_id = update.message.photo[-1].file_id
        
        conn = get_db_connection()
        conn.execute('UPDATE products SET image_id2 = ? WHERE id = ?', (photo_id, product_id))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            "✅ Second image saved!\n\n"
            "Now you can add map coordinates (optional).\n"
            "Enter coordinates in format:\n"
            "`59.4370, 24.7536`\n\n"
            "Or send 'skip' to skip.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
            ]])
        )
        context.user_data['admin_mode'] = 'adding_product_coordinates'

async def handle_edit_image1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Esimese pildi muutmise handler"""
    if update.message.photo:
        product_id = context.user_data.get('editing_product_id')
        photo_id = update.message.photo[-1].file_id
        
        conn = get_db_connection()
        conn.execute('UPDATE products SET image_id = ? WHERE id = ?', (photo_id, product_id))
        conn.commit()
        conn.close()
        
        await update.message.reply_text("✅ First image updated!")
        # Clear editing state
        if 'editing_product_id' in context.user_data:
            del context.user_data['editing_product_id']
        if 'editing_field' in context.user_data:
            del context.user_data['editing_field']

async def handle_edit_image2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Teise pildi muutmise handler"""
    if update.message.photo:
        product_id = context.user_data.get('editing_product_id')
        photo_id = update.message.photo[-1].file_id
        
        conn = get_db_connection()
        conn.execute('UPDATE products SET image_id2 = ? WHERE id = ?', (photo_id, product_id))
        conn.commit()
        conn.close()
        
        await update.message.reply_text("✅ Second image updated!")
        # Clear editing state
        if 'editing_product_id' in context.user_data:
            del context.user_data['editing_product_id']
        if 'editing_field' in context.user_data:
            del context.user_data['editing_field']

async def handle_image2_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Teise pildi küsimise handler"""
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
                "`59.4370, 24.7536`\n\n"
                "Or send 'skip' to skip.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Product Management", callback_data="admin_products")
                ]])
            )
        else:
            await update.message.reply_text("Please send 'yes' to add second image or 'no' to skip:")

async def handle_product_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ühendatud pildihandler kõikidele piltidele"""
    if not update.message.photo:
        return
    
    admin_mode = context.user_data.get('admin_mode')
    editing_field = context.user_data.get('editing_field')
    
    # Toote lisamise protsess
    if admin_mode == 'adding_product_image1':
        await handle_product_image1(update, context)
    elif admin_mode == 'adding_product_image2':
        await handle_product_image2(update, context)
    # Olemasoleva toote muutmine
    elif editing_field == 'image1':
        await handle_edit_image1(update, context)
    elif editing_field == 'image2':
        await handle_edit_image2(update, context)

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
            f"💰 {format_price_display(product['price'])}\n"
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

async def handle_product_field_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toote väljade muutmise handler"""
    if 'editing_product_id' in context.user_data and 'editing_field' in context.user_data:
        product_id = context.user_data['editing_product_id']
        field = context.user_data['editing_field']
        new_value = update.message.text
        
        conn = get_db_connection()
        try:
            if field == 'name':
                conn.execute('UPDATE products SET name = ? WHERE id = ?', (new_value, product_id))
                message = "✅ Product name updated!"
            elif field == 'price':
                try:
                    price = float(new_value)
                    conn.execute('UPDATE products SET price = ? WHERE id = ?', (price, product_id))
                    message = "✅ Product price updated!"
                except ValueError:
                    await update.message.reply_text("❌ Invalid price! Enter a number:")
                    return
            elif field == 'description':
                conn.execute('UPDATE products SET description = ? WHERE id = ?', (new_value, product_id))
                message = "✅ Product description updated!"
            elif field == 'quantity':
                try:
                    quantity = int(new_value)
                    conn.execute('UPDATE products SET quantity = ? WHERE id = ?', (quantity, product_id))
                    message = "✅ Product quantity updated!"
                except ValueError:
                    await update.message.reply_text("❌ Invalid quantity! Enter a whole number:")
                    return
            elif field == 'coordinates':
                if new_value.lower() == 'none':
                    conn.execute('UPDATE products SET map_coordinates = NULL WHERE id = ?', (product_id,))
                    message = "✅ Coordinates removed!"
                else:
                    conn.execute('UPDATE products SET map_coordinates = ? WHERE id = ?', (new_value, product_id))
                    message = "✅ Coordinates updated!"
            
            conn.commit()
            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Error updating product field: {e}")
            await update.message.reply_text("❌ Error updating product!")
        finally:
            conn.close()
        
        # Clear editing state
        if 'editing_product_id' in context.user_data:
            del context.user_data['editing_product_id']
        if 'editing_field' in context.user_data:
            del context.user_data['editing_field']
