import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('bot_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Products table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT NOT NULL,
            second_image TEXT,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Discounts table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS discounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            percentage REAL NOT NULL,
            max_uses INTEGER DEFAULT -1,
            used INTEGER DEFAULT 0,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Orders table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            payment_method TEXT,
            discount_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Cart table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Content table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    
    # Settings table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    
    # Payment methods table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payment_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT UNIQUE NOT NULL,
            enabled BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Insert default content
    conn.execute('''
        INSERT OR IGNORE INTO content (key, value) 
        VALUES 
        ('welcome_message', 'Welcome to our store! 🛍️'),
        ('success_message', 'Thank you for your purchase! ✅')
    ''')
    
    # Insert default exchange rate
    conn.execute('''
        INSERT OR IGNORE INTO settings (key, value) 
        VALUES ('exchange_rate', '1.07')
    ''')
    
    # Insert default payment methods
    conn.execute('''
        INSERT OR IGNORE INTO payment_methods (method, enabled) 
        VALUES 
        ('crypto', TRUE),
        ('bank_transfer', TRUE),
        ('paypal', TRUE)
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def add_user(user_id: int, username: str, first_name: str, last_name: str = None):
    """Add user to database"""
    conn = get_db_connection()
    conn.execute(
        'INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)',
        (user_id, username, first_name, last_name)
    )
    conn.commit()
    conn.close()

def get_products(active_only: bool = True) -> List[Dict]:
    """Get all products"""
    conn = get_db_connection()
    if active_only:
        products = conn.execute('SELECT * FROM products WHERE active = TRUE').fetchall()
    else:
        products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return [dict(product) for product in products]

def get_product(product_id: int) -> Optional[Dict]:
    """Get product by ID"""
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    return dict(product) if product else None

def add_product(name: str, description: str, price: float, image: str, second_image: str = None):
    """Add product to database"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO products (name, description, price, image, second_image) VALUES (?, ?, ?, ?, ?)',
        (name, description, price, image, second_image)
    )
    conn.commit()
    conn.close()

def delete_product(product_id: int):
    """Delete product from database"""
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

def get_discounts() -> List[Dict]:
    """Get all discounts"""
    conn = get_db_connection()
    discounts = conn.execute('SELECT * FROM discounts').fetchall()
    conn.close()
    return [dict(discount) for discount in discounts]

def get_discount(code: str) -> Optional[Dict]:
    """Get discount by code"""
    conn = get_db_connection()
    discount = conn.execute(
        'SELECT * FROM discounts WHERE code = ? AND active = TRUE', 
        (code,)
    ).fetchone()
    conn.close()
    return dict(discount) if discount else None

def add_discount(code: str, percentage: float, max_uses: int = -1):
    """Add discount to database"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO discounts (code, percentage, max_uses) VALUES (?, ?, ?)',
        (code, percentage, max_uses)
    )
    conn.commit()
    conn.close()

def update_discount_usage(code: str):
    """Update discount usage count"""
    conn = get_db_connection()
    conn.execute(
        'UPDATE discounts SET used = used + 1 WHERE code = ?',
        (code,)
    )
    conn.commit()
    conn.close()

def get_content() -> Dict[str, str]:
    """Get all content"""
    conn = get_db_connection()
    content_rows = conn.execute('SELECT * FROM content').fetchall()
    conn.close()
    return {row['key']: row['value'] for row in content_rows}

def update_content(key: str, value: str):
    """Update content"""
    conn = get_db_connection()
    conn.execute(
        'INSERT OR REPLACE INTO content (key, value) VALUES (?, ?)',
        (key, value)
    )
    conn.commit()
    conn.close()

def get_exchange_rate() -> float:
    """Get current exchange rate"""
    conn = get_db_connection()
    result = conn.execute(
        "SELECT value FROM settings WHERE key = 'exchange_rate'"
    ).fetchone()
    conn.close()
    return float(result['value']) if result else 1.0

def update_exchange_rate(rate: float):
    """Update exchange rate"""
    conn = get_db_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES ('exchange_rate', ?)",
        (str(rate),)
    )
    conn.commit()
    conn.close()

def get_admin_stats() -> Dict[str, Any]:
    """Get admin statistics"""
    conn = get_db_connection()
    
    total_users = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
    total_orders = conn.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'completed'").fetchone()['count']
    total_revenue_result = conn.execute("SELECT SUM(amount) as total FROM orders WHERE status = 'completed'").fetchone()
    total_revenue = total_revenue_result['total'] if total_revenue_result['total'] else 0
    active_products = conn.execute("SELECT COUNT(*) as count FROM products WHERE active = TRUE").fetchone()['count']
    active_discounts = conn.execute("SELECT COUNT(*) as count FROM discounts WHERE active = TRUE").fetchone()['count']
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'active_products': active_products,
        'active_discounts': active_discounts
    }

def get_payment_methods() -> List[Dict]:
    """Get all payment methods"""
    conn = get_db_connection()
    methods = conn.execute('SELECT * FROM payment_methods').fetchall()
    conn.close()
    return [dict(method) for method in methods]

def toggle_payment_method(method: str, enabled: bool):
    """Toggle payment method"""
    conn = get_db_connection()
    conn.execute(
        'INSERT OR REPLACE INTO payment_methods (method, enabled) VALUES (?, ?)',
        (method, enabled)
    )
    conn.commit()
    conn.close()

def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    """Add product to cart"""
    conn = get_db_connection()
    
    # Check if item already in cart
    existing = conn.execute(
        'SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
        (user_id, product_id)
    ).fetchone()
    
    if existing:
        conn.execute(
            'UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?',
            (quantity, user_id, product_id)
        )
    else:
        conn.execute(
            'INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
            (user_id, product_id, quantity)
        )
    
    conn.commit()
    conn.close()

def get_cart(user_id: int) -> List[Dict]:
    """Get user cart"""
    conn = get_db_connection()
    cart_items = conn.execute('''
        SELECT c.*, p.name, p.price, p.image 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(item) for item in cart_items]

def clear_cart(user_id: int):
    """Clear user cart"""
    conn = get_db_connection()
    conn.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def create_order(user_id: int, product_id: int, quantity: int, amount: float, 
                payment_method: str, discount_code: str = None):
    """Create order"""
    conn = get_db_connection()
    conn.execute(
        '''INSERT INTO orders 
        (user_id, product_id, quantity, amount, payment_method, discount_code) 
        VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, product_id, quantity, amount, payment_method, discount_code)
    )
    order_id = conn.lastrowid
    conn.commit()
    conn.close()
    return order_id

def get_user_orders(user_id: int) -> List[Dict]:
    """Get user orders"""
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT o.*, p.name, p.image 
        FROM orders o 
        JOIN products p ON o.product_id = p.id 
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(order) for order in orders]
