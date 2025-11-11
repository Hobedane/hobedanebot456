import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import update_order_delivery, update_product_stock, get_product, get_order

logger = logging.getLogger(__name__)

async def payment_approval(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    order_id = int(data[2])
    action = data[3]
    
    if action == 'approve':
        order = get_order(order_id)
        if order:
            # Update product stock
            update_product_stock(order['product_id'], order['quantity'])
            
            # Send product details to customer
            product = get_product(order['product_id'])
            if product:
                customer_user_id = order['customer_user_id']
                
                # Saada kliendile KÕIK pildid ja koordinaadid
                try:
                    # Esimene pilt
                    if product['image']:
                        await context.bot.send_photo(
                            chat_id=customer_user_id,
                            photo=product['image'],
                            caption="🎉 Your purchase has been confirmed!\n\nHere is your product:"
                        )
                    
                    # Teine pilt (kui on olemas)
                    if product.get('second_image'):
                        await context.bot.send_photo(
                            chat_id=customer_user_id,
                            photo=product['second_image'],
                            caption="Additional product image:"
                        )
                    
                    # Koordinaadid/asukoht (kui on olemas)
                    if product.get('location'):
                        location_message = (
                            f"📍 Product Location/Coordinates:\n"
                            f"{product['location']}\n\n"
                            f"📦 Product: {product['name']}\n"
                            f"💰 Amount Paid: €{order['amount']:.2f}"
                        )
                        await context.bot.send_message(
                            chat_id=customer_user_id,
                            text=location_message
                        )
                    else:
                        # Kui koordinaate pole
                        await context.bot.send_message(
                            chat_id=customer_user_id,
                            text=f"📍 Location information will be provided separately.\n\n"
                                 f"📦 Product: {product['name']}\n"
                                 f"💰 Amount Paid: €{order['amount']:.2f}"
                        )
                    
                    # Update order with delivery info
                    delivery_info = f"Product details sent to customer. Location: {product.get('location', 'Not specified')}"
                    update_order_delivery(order_id, delivery_info)
                    
                    await query.edit_message_text("✅ Payment approved and product details sent to customer!")
                    
                except Exception as e:
                    logger.error(f"Failed to send product details to customer: {e}")
                    await query.edit_message_text("✅ Payment approved but failed to send product details to customer.")
            else:
                await query.edit_message_text("❌ Product not found.")
        else:
            await query.edit_message_text("❌ Order not found.")
    
    elif action == 'reject':
        await query.edit_message_text("❌ Payment rejected.")
