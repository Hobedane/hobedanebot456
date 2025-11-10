import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection
from config import ADMIN_USER_ID, logger

async def admin_approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    order_id = query.data.replace("approve_", "")
    
    # Confirmation prompt
    keyboard = [
        [
            InlineKeyboardButton("✅ YES, confirm payment", callback_data=f"confirm_approve_{order_id}"),
            InlineKeyboardButton("❌ NO, cancel", callback_data=f"cancel_approve_{order_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔍 CONFIRMATION\n\n"
        f"Are you sure you want to approve this payment?\n\n"
        f"🆔 Order ID: {order_id}",
        reply_markup=reply_markup
    )

async def confirm_approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    order_id = query.data.replace("confirm_approve_", "")
    
    conn = get_db_connection()
    # Find order (or orders for cart)
    if '_' in order_id:
        # Cart order - all orders with same prefix
        base_order_id = order_id.split('_')[0]
        orders = conn.execute('SELECT * FROM orders WHERE order_id LIKE ?', (f"{base_order_id}%",)).fetchall()
    else:
        # Single order
        orders = conn.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,)).fetchall()
    
    if not orders:
        await query.edit_message_text("❌ Order not found!")
        return
    
    # Update all orders status
    for order in orders:
        conn.execute('UPDATE orders SET status = ? WHERE order_id = ?', ('completed', order['order_id']))
        # Reduce product quantity
        product = conn.execute('SELECT * FROM products WHERE id = ?', (order['product_id'],)).fetchone()
        new_quantity = product['quantity'] - 1
        if new_quantity <= 0:
            conn.execute('UPDATE products SET quantity = 0, active = 0 WHERE id = ?', (product['id'],))
        else:
            conn.execute('UPDATE products SET quantity = ? WHERE id = ?', (new_quantity, product['id']))
    
    conn.commit()
    
    # Send images and message to client
    client_id = orders[0]['client_id']
    try:
        success_content = conn.execute('SELECT * FROM content WHERE key = ?', ('success_message',)).fetchone()
        for order in orders:
            product = conn.execute('SELECT * FROM products WHERE id = ?', (order['product_id'],)).fetchone()
            if product:
                caption = f"🛍️ {product['name']}\n📝 {product['description']}\n\n{success_content['content']}"
                # Add map coordinates if available
                if product['map_coordinates']:
                    caption += f"\n\n📍 Location: {product['map_coordinates']}"
                
                # Send both images if available
                images_sent = 0
                if product['image_id'] and product['image_id'].strip() and product['image_id'] != 'None':
                    try:
                        await context.bot.send_photo(
                            chat_id=client_id,
                            photo=product['image_id'],
                            caption=caption if images_sent == 0 else None
                        )
                        images_sent += 1
                    except Exception as e:
                        logger.error(f"Error sending first image: {e}")
                
                if product['image_id2'] and product['image_id2'].strip() and product['image_id2'] != 'None':
                    try:
                        await context.bot.send_photo(
                            chat_id=client_id,
                            photo=product['image_id2'],
                            caption=caption if images_sent == 0 else None
                        )
                        images_sent += 1
                    except Exception as e:
                        logger.error(f"Error sending second image: {e}")
                
                # If no images were sent, send text message
                if images_sent == 0:
                    await context.bot.send_message(
                        chat_id=client_id,
                        text=caption
                    )
    except Exception as e:
        logger.error(f"Error notifying client: {e}")
        # Send fallback message
        try:
            await context.bot.send_message(
                chat_id=client_id,
                text=f"✅ Your payment has been confirmed! Order ID: {order_id}"
            )
        except Exception as e2:
            logger.error(f"Error sending fallback message: {e2}")
    
    conn.close()
    
    # Notify admin
    await query.edit_message_text(
        f"✅ PAYMENT APPROVED!\n\n"
        f"🆔 Order ID: {order_id}\n"
        f"👤 Products and message sent to client\n"
        f"⏰ Approved: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )

async def cancel_approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Payment approval cancelled.")

async def admin_reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    order_id = query.data.replace("reject_", "")
    
    # Confirmation prompt
    keyboard = [
        [
            InlineKeyboardButton("✅ YES, reject payment", callback_data=f"confirm_reject_{order_id}"),
            InlineKeyboardButton("❌ NO, cancel", callback_data=f"cancel_reject_{order_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔍 CONFIRMATION\n\n"
        f"Are you sure you want to reject this payment?\n\n"
        f"🆔 Order ID: {order_id}",
        reply_markup=reply_markup
    )

async def confirm_reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    order_id = query.data.replace("confirm_reject_", "")
    
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE order_id = ?', ('rejected', order_id))
    conn.commit()
    conn.close()
    
    await query.edit_message_text(
        f"❌ PAYMENT REJECTED!\n\n"
        f"🆔 Order ID: {order_id}\n"
        f"⏰ Rejected: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        f"Client will be notified that payment was not visible."
    )

async def cancel_reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Payment rejection cancelled.")
