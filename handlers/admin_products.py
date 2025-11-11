import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, CommandHandler

from database import get_product, get_all_products, add_product, update_product, delete_product
from config import PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_DESCRIPTION, PRODUCT_QUANTITY, PRODUCT_IMAGE, PRODUCT_SECOND_IMAGE, PRODUCT_COORDINATES, CONFIRM_ADD_PRODUCT, ADMIN_PRODUCTS

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def admin_products(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Add Product", callback_data="add_product")],
        [InlineKeyboardButton("Edit Product", callback_data="edit_product")],
        [InlineKeyboardButton("Delete Product", callback_data="delete_product")],
        [InlineKeyboardButton("Back to Admin", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        "Product Management:\n\n"
        "• Add Product: Create new product listings\n"
        "• Edit Product: Modify existing products\n"
        "• Delete Product: Remove products from store",
        reply_markup=reply_markup
    )
    
    return ADMIN_PRODUCTS

def start_add_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    context.user_data['new_product'] = {}
    
    query.edit_message_text("Please enter the product name:")
    
    return PRODUCT_NAME

def process_product_name(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    name = update.message.text
    
    context.user_data['new_product']['name'] = name
    
    update.message.reply_text("Please enter the price for the product:")
    
    return PRODUCT_PRICE

def process_product_price(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    price = update.message.text
    
    # Validate price
    try:
        price = float(price)
        if price <= 0:
            update.message.reply_text("Price must be a positive number. Please enter a valid price:")
            return PRODUCT_PRICE
    except ValueError:
        update.message.reply_text("Please enter a valid number for price:")
        return PRODUCT_PRICE
    
    context.user_data['new_product']['price'] = price
    
    update.message.reply_text("Please enter the description for the product:")
    
    return PRODUCT_DESCRIPTION

def process_product_description(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    description = update.message.text
    
    context.user_data['new_product']['description'] = description
    
    update.message.reply_text("Please enter the quantity for the product:")
    
    return PRODUCT_QUANTITY

def process_quantity(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    quantity_text = update.message.text
    
    # Validate quantity
    try:
        quantity = int(quantity_text)
        if quantity < 0:
            update.message.reply_text("Quantity must be a non-negative integer. Please enter a valid quantity:")
            return PRODUCT_QUANTITY
    except ValueError:
        update.message.reply_text("Please enter a valid integer for quantity:")
        return PRODUCT_QUANTITY
    
    context.user_data['new_product']['quantity'] = quantity
    
    # Ask for main product image
    update.message.reply_text("Please send the main image for the product:")
    
    return PRODUCT_IMAGE

def process_product_image(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo = update.message.photo[-1]
    
    context.user_data['new_product']['image'] = photo.file_id
    
    # Ask for optional second image
    update.message.reply_text("Would you like to add a second image? Send the image or type /skip to continue:")
    
    return PRODUCT_SECOND_IMAGE

def process_product_image_text(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text("You didn't send an image. Please send an image for the product or type /cancel to cancel.")
    return PRODUCT_IMAGE

def process_second_image(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo = update.message.photo[-1]
    
    context.user_data['new_product']['second_image'] = photo.file_id
    
    # Ask for coordinates
    update.message.reply_text("Please enter the coordinates/location for the product (e.g., '58.1234, 25.1234' or 'Tartu, Estonia'):")
    
    return PRODUCT_COORDINATES

def skip_second_image(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['new_product']['second_image'] = None
    
    # Ask for coordinates
    update.message.reply_text("Please enter the coordinates/location for the product (e.g., '58.1234, 25.1234' or 'Tartu, Estonia'):")
    
    return PRODUCT_COORDINATES

def process_second_image_text(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    
    if text.lower() == '/skip':
        return skip_second_image(update, context)
    
    update.message.reply_text("Please send an image or type /skip to continue:")
    return PRODUCT_SECOND_IMAGE

def process_coordinates(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    coordinates = update.message.text
    
    context.user_data['new_product']['coordinates'] = coordinates
    
    return ask_confirm_add_product(update, context)

def ask_confirm_add_product(update: Update, context: CallbackContext) -> int:
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
        update.message.reply_photo(photo=product['image'], caption=text, reply_markup=reply_markup)
    else:
        update.message.reply_text(text, reply_markup=reply_markup)
    
    return CONFIRM_ADD_PRODUCT

def confirm_add_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
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
        
        query.edit_message_text("Product added successfully!")
    else:
        query.edit_message_text("Product addition cancelled.")
    
    # Clear user_data
    context.user_data.pop('new_product', None)
    
    return ConversationHandler.END

def edit_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    products = get_all_products()
    
    if not products:
        query.edit_message_text("No products available to edit.")
        return ConversationHandler.END
    
    keyboard = []
    for product in products:
        keyboard.append([InlineKeyboardButton(product['name'], callback_data=f"edit_{product['id']}")])
    
    keyboard.append([InlineKeyboardButton("Back", callback_data="products")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text("Select a product to edit:", reply_markup=reply_markup)
    
    return ADMIN_PRODUCTS

def delete_product_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    products = get_all_products()
    
    if not products:
        query.edit_message_text("No products available to delete.")
        return ConversationHandler.END
    
    keyboard = []
    for product in products:
        keyboard.append([InlineKeyboardButton(product['name'], callback_data=f"delete_{product['id']}")])
    
    keyboard.append([InlineKeyboardButton("Back", callback_data="products")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text("Select a product to delete:", reply_markup=reply_markup)
    
    return ADMIN_PRODUCTS

def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data.pop('new_product', None)
    update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def admin_products_conv() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_products, pattern='^products$')],
        states={
            ADMIN_PRODUCTS: [
                CallbackQueryHandler(admin_products, pattern='^products$'),
                CallbackQueryHandler(start_add_product, pattern='^add_product$'),
                CallbackQueryHandler(edit_product, pattern='^edit_product$'),
                CallbackQueryHandler(delete_product_handler, pattern='^delete_product$'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        map_to_parent={
            ConversationHandler.END: ADMIN_PRODUCTS
        }
    )

def add_product_conv() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_product, pattern='^add_product$')],
        states={
            PRODUCT_NAME: [MessageHandler(Filters.text & ~Filters.command, process_product_name)],
            PRODUCT_PRICE: [MessageHandler(Filters.text & ~Filters.command, process_product_price)],
            PRODUCT_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, process_product_description)],
            PRODUCT_QUANTITY: [MessageHandler(Filters.text & ~Filters.command, process_quantity)],
            PRODUCT_IMAGE: [
                MessageHandler(Filters.photo, process_product_image),
                MessageHandler(Filters.text & ~Filters.command, process_product_image_text)
            ],
            PRODUCT_SECOND_IMAGE: [
                MessageHandler(Filters.photo, process_second_image),
                MessageHandler(Filters.text & ~Filters.command, process_second_image_text)
            ],
            PRODUCT_COORDINATES: [MessageHandler(Filters.text & ~Filters.command, process_coordinates)],
            CONFIRM_ADD_PRODUCT: [CallbackQueryHandler(confirm_add_product, pattern='^(confirm|cancel)_product$')]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        map_to_parent={
            ConversationHandler.END: ADMIN_PRODUCTS
        }
    )
