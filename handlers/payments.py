import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler

from database import get_order_items, update_order_status, get_user

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def send_product_content(context: CallbackContext, user_id: int, order_id: int):
    """Send product content (images and coordinates) to user after payment"""
    try:
        order_items = get_order_items(order_id)
        
        for item in order_items:
            # Send main image
            if item['image']:
                context.bot.send_photo(
                    chat_id=user_id,
                    photo=item['image'],
                    caption=f"🎉 {item['name']} - Your purchased product!"
                )
            
            # Send second image if available
            if item.get('second_image'):
                context.bot.send_photo(
                    chat_id=user_id,
                    photo=item['second_image'],
                    caption=f"📸 Additional image for {item['name']}"
                )
            
            # Send coordinates if available
            if item.get('coordinates'):
                context.bot.send_message(
                    chat_id=user_id,
                    text=f"📍 Location for {item['name']}:\n{item['coordinates']}"
                )
        
        # Mark order as completed
        update_order_status(order_id, 'completed')
        
    except Exception as e:
        logger.error(f"Error sending product content: {e}")
