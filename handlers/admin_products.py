import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import add_product, get_products, delete_product

logger = logging.getLogger(__name__)

# States for product conversation
PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_PRICE, PRODUCT_IMAGE, PRODUCT_SECOND_IMAGE, PRODUCT_CONFIRM = range(6)

async def admin_products(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Add Product", callback_data='add_product')],
        [InlineKeyboardButton("View Products", callback_data='view_products')],
        [InlineKeyboardButton("Delete Product", callback_data='delete_product')],
        [InlineKeyboardButton("Back", callback_data='admin_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Product Management:", reply_markup=reply_markup)

async def add_product_start(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    # Clear any existing data
    context.user_data.clear()
    await query.edit_message_text("Enter product name:")
    return PRODUCT_NAME

async def add_product_name(update: Update, context: CallbackContext) -> int:
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("Please enter a valid product name:")
        return PRODUCT_NAME
    
    context.user_data['product_name'] = name
    await update.message.reply_text("Enter product description:")
    return PRODUCT_DESCRIPTION

async def add_product_description(update: Update, context: CallbackContext) -> int:
    description = update.message.text.strip()
    if not description:
        await update.message.reply_text("Please enter a valid product description:")
        return PRODUCT_DESCRIPTION
    
    context.user_data['product_description'] = description
    await update.message.reply_text("Enter product price (in EUR):")
    return PRODUCT_PRICE

async def add_product_price(update: Update, context: CallbackContext) -> int:
    try:
        price = float(update.message.text.strip())
        if price <= 0:
            await update.message.reply_text("Please enter a positive price:")
            return PRODUCT_PRICE
    except ValueError:
        await update.message.reply_text("Invalid price. Please enter a number:")
        return PRODUCT_PRICE
    
    context.user_data['product_price'] = price
    await update.message.reply_text("Send product image (photo):")
    return PRODUCT_IMAGE

async def add_product_image(update: Update, context: CallbackContext) -> int:
    if not update.message.photo:
        await update.message.reply_text("Please send a photo:")
        return PRODUCT_IMAGE
    
    photo = update.message.photo[-1]
    context.user_data['product_image'] = photo.file_id
    
    keyboard = [
        [InlineKeyboardButton("Add Second Image", callback_data='add_second_image')],
        [InlineKeyboardButton("Skip Second Image", callback_data='skip_second_image')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "First image received! Would you like to add a second image?",
        reply_markup=reply_markup
    )
    return PRODUCT_SECOND_IMAGE

async def add_second_image_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add_second_image':
        await query.edit_message_text("Please send the second image:")
        return PRODUCT_SECOND_IMAGE
    else:  # skip_second_image
        context.user_data['product_second_image'] = None
        return await add_product_confirm(update, context)

async def add_second_image_input(update: Update, context: CallbackContext) -> int:
    if not update.message.photo:
        await update.message.reply_text("Please send a photo:")
        return PRODUCT_SECOND_IMAGE
    
    photo = update.message.photo[-1]
    context.user_data['product_second_image'] = photo.file_id
    return await add_product_confirm(update, context)

async def add_product_confirm(update: Update, context: CallbackContext) -> int:
    name = context.user_data['product_name']
    description = context.user_data['product_description']
    price = context.user_data['product_price']
    image = context.user_data['product_image']
    second_image = context.user_data.get('product_second_image')
    
    text = (
        f"Product Details:\n\n"
        f"Name: {name}\n"
        f"Description: {description}\n"
        f"Price: €{price:.2f}\n"
        f"Images: {2 if second_image else 1}\n\n"
        f"Confirm adding this product?"
    )
    
    keyboard = [
        [InlineKeyboardButton("Confirm", callback_data='confirm_product')],
        [InlineKeyboardButton("Cancel", callback_data='cancel_product')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    return PRODUCT_CONFIRM

async def add_product_confirm_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_product':
        name = context.user_data['product_name']
        description = context.user_data['product_description']
        price = context.user_data['product_price']
        image = context.user_data['product_image']
        second_image = context.user_data.get('product_second_image')
        
        add_product(name, description, price, image, second_image)
        await query.edit_message_text("✅ Product added successfully!")
    else:
        await query.edit_message_text("❌ Product addition canceled.")
    
    return ConversationHandler.END

async def view_products(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    products = get_products()
    if not products:
        await query.edit_message_text("No products found.")
        return
    
    text = "📦 All Products:\n\n"
    for product in products:
        text += (
            f"Name: {product['name']}\n"
            f"Price: €{product['price']:.2f}\n"
            f"Description: {product['description'][:100]}...\n"
            f"────────────────────\n"
        )
    
    keyboard = [[InlineKeyboardButton("Back", callback_data='admin_products')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def delete_product_start(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    products = get_products()
    if not products:
        await query.edit_message_text("No products to delete.")
        return
    
    keyboard = []
    for product in products:
        keyboard.append([InlineKeyboardButton(
            f"{product['name']} - €{product['price']:.2f}", 
            callback_data=f"delete_product_{product['id']}"
        )])
    keyboard.append([InlineKeyboardButton("Back", callback_data='admin_products')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select product to delete:", reply_markup=reply_markup)

async def delete_product_confirm(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split('_')[-1])
    delete_product(product_id)
    await query.edit_message_text("✅ Product deleted successfully!")

async def cancel_product(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Product addition canceled.')
    return ConversationHandler.END
