import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler

from database import get_order_items, update_order_status, get_order

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def payments(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Payment Methods", callback_data="payment_methods")],
        [InlineKeyboardButton("Payment History", callback_data="payment_history")],
        [InlineKeyboardButton("Back to Main", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        "Payments Section:\n\n"
        "• Payment Methods: Configure payment options\n"
        "• Payment History: View your payment history",
        reply_markup=reply_markup
    )
    
    return "PAYMENTS"

def payment_methods(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Bank Transfer", callback_data="bank_transfer")],
        [InlineKeyboardButton("Crypto", callback_data="crypto_payment")],
        [InlineKeyboardButton("Other", callback_data="other_payment")],
        [InlineKeyboardButton("Back", callback_data="payments")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        "Available Payment Methods:\n\n"
        "• Bank Transfer: Traditional bank transfer\n"
        "• Crypto: Cryptocurrency payments\n"
        "• Other: Other payment options",
        reply_markup=reply_markup
    )
    
    return "PAYMENT_METHODS"

def payment_history(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    # Here you would fetch actual payment history from database
    # For now, using placeholder text
    payment_history_text = "Your recent payments:\n\n• Order #001 - $50.00 - Completed\n• Order #002 - $75.00 - Completed"
    
    keyboard = [
        [InlineKeyboardButton("Back", callback_data="payments")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(payment_history_text, reply_markup=reply_markup)
    
    return "PAYMENT_HISTORY"

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

def complete_payment(update: Update, context: CallbackContext):
    """Complete payment and send product content to user"""
    query = update.callback_query
    query.answer()
    
    # Get order_id from callback data (assuming format: "complete_payment_{order_id}")
    order_id = int(query.data.split('_')[2])
    
    # Update order status to paid
    update_order_status(order_id, 'paid')
    
    # Get user_id from order
    order = get_order(order_id)
    user_id = order[1]  # Assuming user_id is at index 1
    
    # Send product content to user
    send_product_content(context, user_id, order_id)
    
    query.edit_message_text("Payment completed and product content sent to customer!")
