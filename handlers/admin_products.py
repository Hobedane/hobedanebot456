import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from database import get_product, get_all_products, add_product, update_product, delete_product
from config import PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_DESCRIPTION, PRODUCT_QUANTITY, PRODUCT_IMAGE, PRODUCT_SECOND_IMAGE, PRODUCT_COORDINATES, CONFIRM_ADD_PRODUCT

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def admin_products(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Add Product", callback_data="admin_add_product")],
        [InlineKeyboardButton("Edit Product", callback_data="admin_edit_product")],
        [InlineKeyboardButton("Delete Product", callback_data="admin_delete_product")],
        [InlineKeyboardButton("Back to Admin", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Product Management:\n\n"
        "• Add Product: Create new product listings\n"
        "• Edit Product: Modify existing products\n"
        "• Delete Product: Remove products from store",
        reply_markup=reply_markup
    )
    
    return PRODUCT_NAME

async def admin_add_product_start(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    context.user_data['new_product'] = {}
    context.user_data['admin_mode'] = 'adding_product_name'
    
    await query.edit_message_text("Please enter the product name:")
    
    return PRODUCT_NAME

async def handle_product_name(update: Update, context: CallbackContext) -> int:
    name = update.message.text
    
    context.user_data['new_product']['name'] = name
    context.user_data['admin_mode'] = 'adding_product_price'
    
    await update.message.reply_text("Please enter the price for the product:")
    
    return PRODUCT_PRICE

async def handle_product_price(update: Update, context: CallbackContext) -> int:
    price_text = update.message.text
    
    # Validate price
    try:
        price = float(price_text)
        if price <= 0:
            await update.message.reply_text("Price must be a positive number. Please enter a valid price:")
            return PRODUCT_PRICE
    except ValueError:
        await update.message.reply_text("Please enter a valid number for price:")
        return PRODUCT_PRICE
    
    context.user_data['new_product']['price'] = price
    context.user_data['admin_mode'] = 'adding_product_description'
    
    await update.message.reply_text("Please enter the description for the product:")
    
    return PRODUCT_DESCRIPTION

async def handle_product_description(update: Update, context: CallbackContext) -> int:
    description = update.message.text
    
    context.user_data['new_product']['description'] = description
    context.user_data['admin_mode'] = 'adding_product_quantity'
    
    await update.message.reply_text("Please enter the quantity for the product:")
    
    return PRODUCT_QUANTITY

async def handle_product_quantity(update: Update, context: CallbackContext) -> int:
    quantity_text = update.message.text
    
    # Validate quantity - PARANDATUD OSA!
    try:
        quantity = int(quantity_text)
        if quantity < 0:
            await update.message.reply_text("Quantity must be a non-negative integer. Please enter a valid quantity:")
            return PRODUCT_QUANTITY
    except ValueError:
        await update.message.reply_text("Please enter a valid integer for quantity:")
        return PRODUCT_QUANTITY
    
    context.user_data['new_product']['quantity'] = quantity
    context.user_data['admin_mode'] = 'adding_product_image1'
    
    await update.message.reply_text("Please send the main image for the product:")
    
    return PRODUCT_IMAGE

async def handle_product_image1(update: Update, context: CallbackContext) -> int:
    if update.message.photo:
        photo = update.message.photo[-1]
        context.user_data['new_product']['image'] = photo.file_id
        context.user_data['admin_mode'] = 'adding_product_image2_choice'
        
        keyboard = [
            [InlineKeyboardButton("Add Second Image", callback_data="add_second_image")],
            [InlineKeyboardButton("Skip Second Image", callback_data="skip_second_image")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text("Would you like to add a second image?", reply_markup=reply_markup)
        
        return PRODUCT_SECOND_IMAGE
    else:
        await update.message.reply_text("Please send an image for the product.")
        return PRODUCT_IMAGE

async def handle_image2_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add_second_image':
        context.user_data['admin_mode'] = 'adding_product_image2'
        await query.edit_message_text("Please send the second image for the product:")
        return PRODUCT_SECOND_IMAGE
    else:
        context.user_data['new_product']['second_image'] = None
        context.user_data['admin_mode'] = 'adding_product_coordinates'
        await query.edit_message_text("Please enter the coordinates/location for the product (e.g., '58.1234, 25.1234' or 'Tartu, Estonia'):")
        return PRODUCT_COORDINATES

async def handle_product_image2(update: Update, context: CallbackContext) -> int:
    if update.message.photo:
        photo = update.message.photo[-1]
        context.user_data['new_product']['second_image'] = photo.file_id
        context.user_data['admin_mode'] = 'adding_product_coordinates'
        
        await update.message.reply_text("Please enter the coordinates/location for the product (e.g., '58.1234, 25.1234' or 'Tartu, Estonia'):")
        
        return PRODUCT_COORDINATES
    else:
        await update.message.reply_text("Please send an image for the product.")
        return PRODUCT_SECOND_IMAGE

async def handle_product_coordinates(update: Update, context: CallbackContext) -> int:
    coordinates = update.message.text
    
    context.user_data['new_product']['coordinates'] = coordinates
    context.user_data['admin_mode'] = None
    
    # Show confirmation
    product = context.user_data['new_product']
    
    text = (
        f"Please confirm the product details:\n\n"
        f"Name: {product['name']}\n"
        f"Price: {product['price']}\n"
        f"Description: {product['description']}\n"
        f"Quantity: {product['quantity']}\n"
        f"Coordinates: {product.get('coordinates', 'Not provided')}\n"
        f"Second Image: {'Provided' if product.get('second_image') else 'Not added'}"
    )
    
    keyboard = [
        [InlineKeyboardButton("Confirm", callback_data="confirm_product"),
         InlineKeyboardButton("Cancel", callback_data="cancel_product")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if 'image' in product:
        await update.message.reply_photo(photo=product['image'], caption=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    return CONFIRM_ADD_PRODUCT

async def confirm_add_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_product':
        product = context.user_data['new_product']
        
        # Add product to database
        add_product(
            name=product['name'],
            price=product['price'],
            description=product['description'],
            quantity=product['quantity'],
            image=product.get('image'),
            second_image=product.get('second_image'),
            coordinates=product.get('coordinates')
        )
        
        await query.edit_message_text("✅ Product added successfully!")
    else:
        await query.edit_message_text("❌ Product addition cancelled.")
    
    # Clear user_data
    context.user_data.pop('new_product', None)
    context.user_data.pop('admin_mode', None)
    
    return ConversationHandler.END

async def admin_edit_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    # Extract product ID from callback data (format: "admin_edit_product_{id}")
    product_id = int(query.data.split('_')[3])
    
    # Get product from database
    product = get_product(product_id)
    
    if product:
        context.user_data['editing_product'] = product
        context.user_data['admin_mode'] = 'editing_product'
        
        keyboard = [
            [InlineKeyboardButton("Edit Name", callback_data=f"edit_name_{product_id}")],
            [InlineKeyboardButton("Edit Price", callback_data=f"edit_price_{product_id}")],
            [InlineKeyboardButton("Edit Description", callback_data=f"edit_description_{product_id}")],
            [InlineKeyboardButton("Edit Quantity", callback_data=f"edit_quantity_{product_id}")],
            [InlineKeyboardButton("Edit Image", callback_data=f"edit_image_{product_id}")],
            [InlineKeyboardButton("Back to Products", callback_data="admin_products")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Editing Product: {product['name']}\n\n"
            f"Price: ${product['price']}\n"
            f"Quantity: {product['quantity']}\n"
            f"Description: {product['description']}\n\n"
            "Select what you want to edit:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("❌ Product not found!")
    
    return PRODUCT_NAME

async def admin_delete_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    # Extract product ID from callback data (format: "admin_delete_product_{id}")
    product_id = int(query.data.split('_')[3])
    
    # Get product from database
    product = get_product(product_id)
    
    if product:
        keyboard = [
            [InlineKeyboardButton("✅ Confirm Delete", callback_data=f"confirm_delete_{product_id}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="admin_products")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Are you sure you want to delete:\n\n"
            f"Product: {product['name']}\n"
            f"Price: ${product['price']}\n"
            f"Quantity: {product['quantity']}\n\n"
            "This action cannot be undone!",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("❌ Product not found!")
    
    return PRODUCT_NAME

async def confirm_delete_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    # Extract product ID from callback data (format: "confirm_delete_{id}")
    product_id = int(query.data.split('_')[2])
    
    # Delete product from database
    delete_product(product_id)
    
    await query.edit_message_text("✅ Product deleted successfully!")
    
    # Clear user_data
    context.user_data.pop('editing_product', None)
    context.user_data.pop('admin_mode', None)
    
    return ConversationHandler.END

async def cancel_operation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    # Clear user_data
    context.user_data.pop('new_product', None)
    context.user_data.pop('editing_product', None)
    context.user_data.pop('admin_mode', None)
    
    await query.edit_message_text("❌ Operation cancelled.")
    
    return ConversationHandler.END
