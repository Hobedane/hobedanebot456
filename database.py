import sqlite3
import datetime
from config import logger

def init_database():
    conn = sqlite3.connect('poebot.db')
    c = conn.cursor()
    
    # Products - ADDED SECOND IMAGE FIELD
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT NOT NULL, 
        price REAL NOT NULL, 
        description TEXT, 
        image_id TEXT, 
        image_id2 TEXT, 
        quantity INTEGER DEFAULT 1, 
        active BOOLEAN DEFAULT 1, 
        map_coordinates TEXT, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Content (about us, contact, rules etc)
    c.execute('''CREATE TABLE IF NOT EXISTS content (
        key TEXT PRIMARY KEY, 
        title TEXT NOT NULL, 
        content TEXT NOT NULL, 
        active BOOLEAN DEFAULT 1)''')
    
    # Payment settings
    c.execute('''CREATE TABLE IF NOT EXISTS payment_settings (
        crypto_type TEXT PRIMARY KEY, 
        address TEXT NOT NULL, 
        blockchain TEXT NOT NULL, 
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # NEW: Exchange rate table
    c.execute('''CREATE TABLE IF NOT EXISTS exchange_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eur_to_usd REAL NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Discount codes
    c.execute('''CREATE TABLE IF NOT EXISTS discount_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        code TEXT UNIQUE NOT NULL, 
        discount_percent INTEGER NOT NULL, 
        expires DATE, 
        active BOOLEAN DEFAULT 1, 
        used_count INTEGER DEFAULT 0, 
        max_uses INTEGER DEFAULT -1, 
        is_general BOOLEAN DEFAULT 1, 
        client_id INTEGER, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Orders
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        order_id TEXT UNIQUE NOT NULL, 
        client_id INTEGER NOT NULL, 
        product_id INTEGER NOT NULL, 
        status TEXT DEFAULT 'pending', 
        discount_code TEXT, 
        final_price REAL, 
        payment_source_address TEXT, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Shopping cart
    c.execute('''CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER NOT NULL, 
        product_id INTEGER NOT NULL, 
        quantity INTEGER DEFAULT 1, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Add default content (English)
    default_content = [
        ('about_us', 'ℹ️ About Us', 'We are a reliable store offering quality products.', 1),
        ('contact', '📞 Contact', '📧 Email: info@store.com\n📱 Phone: +1 234 567 890\n📍 Address: Example St 1, City', 1),
        ('website', '🌐 Website', 'https://www.ourstore.com', 1),
        ('rules', '📝 Rules', '1. Products shipped within 24h\n2. Returns within 14 days\n3. Customer service: Mon-Fri 9-18', 1),
        ('faq', '🔍 FAQ', 'Q: How fast do you ship?\nA: 1-2 business days\n\nQ: Do you ship internationally?\nA: Yes, worldwide', 1),
        ('success_message', '🎉 Thank you for your purchase!', 'Enjoy your product! We hope it brings you joy! ❤️', 1),
        ('welcome_message', '👋 Welcome', 'Hello! I am your store bot. Choose from the options below:', 1)
    ]
    c.executemany('''INSERT OR IGNORE INTO content (key, title, content, active) VALUES (?, ?, ?, ?)''', default_content)
    
    # Check if payment settings already exist before inserting defaults
    existing_payments = c.execute('SELECT COUNT() FROM payment_settings').fetchone()[0]
    if existing_payments == 0:
        default_payments = [
            ('btc', 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh', 'Bitcoin'),
            ('eth', '0x71C7656EC7ab88b098defB751B7401B5f6d8976F', 'Ethereum')
        ]
        c.executemany('''INSERT INTO payment_settings (crypto_type, address, blockchain) VALUES (?, ?, ?)''', default_payments)
    
    # Insert default exchange rate
    existing_rates = c.execute('SELECT COUNT() FROM exchange_rates').fetchone()[0]
    if existing_rates == 0:
        c.execute('INSERT INTO exchange_rates (eur_to_usd) VALUES (?)', (1.16,))
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('poebot.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_exchange_rate():
    """Get current EUR to USD exchange rate"""
    conn = get_db_connection()
    rate = conn.execute('SELECT eur_to_usd FROM exchange_rates ORDER BY updated_at DESC LIMIT 1').fetchone()
    conn.close()
    return rate['eur_to_usd'] if rate else 1.16

def update_exchange_rate(new_rate):
    """Update EUR to USD exchange rate"""
    conn = get_db_connection()
    conn.execute('INSERT INTO exchange_rates (eur_to_usd) VALUES (?)', (new_rate,))
    conn.commit()
    conn.close()
