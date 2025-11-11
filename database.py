import sqlite3
import logging
from config import DATABASE

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Products table with new fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                quantity INTEGER NOT NULL,
                image TEXT,
                second_image TEXT,
                coordinates TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cart table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Order items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Discounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                discount_type TEXT NOT NULL,
                value REAL NOT NULL,
                min_order REAL,
                max_uses INTEGER,
                used_count INTEGER DEFAULT 0,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

def add_product(name, price, description, quantity, image=None, second_image=None, coordinates=None):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, price, description, quantity, image, second_image, coordinates)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, price, description, quantity, image, second_image, coordinates))
        conn.commit()
        return cursor.lastrowid

def get_product(product_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None

def get_all_products():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def update_product(product_id, name, price, description, quantity, image=None, second_image=None, coordinates=None):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if image and second_image and coordinates:
            cursor.execute('''
                UPDATE products 
                SET name = ?, price = ?, description = ?, quantity = ?, image = ?, second_image = ?, coordinates = ?
                WHERE id = ?
            ''', (name, price, description, quantity, image, second_image, coordinates, product_id))
        elif image and second_image:
            cursor.execute('''
                UPDATE products 
                SET name = ?, price = ?, description = ?, quantity = ?, image = ?, second_image = ?
                WHERE id = ?
            ''', (name, price, description, quantity, image, second_image, product_id))
        elif image:
            cursor.execute('''
                UPDATE products 
                SET name = ?, price = ?, description = ?, quantity = ?, image = ?
                WHERE id = ?
            ''', (name, price, description, quantity, image, product_id))
        else:
            cursor.execute('''
                UPDATE products 
                SET name = ?, price = ?, description = ?, quantity = ?
                WHERE id = ?
            ''', (name, price, description, quantity, product_id))
        conn.commit()

def delete_product(product_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()

def add_user(user_id, username, first_name, last_name):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        conn.commit()

def get_user(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone()

def add_to_cart(user_id, product_id, quantity=1):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Check if item already in cart
        cursor.execute('SELECT * FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?', 
                          (quantity, user_id, product_id))
        else:
            cursor.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)', 
                          (user_id, product_id, quantity))
        conn.commit()

def get_cart(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, p.name, p.price, p.image 
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_id = ?
        ''', (user_id,))
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def update_cart_item(user_id, product_id, quantity):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if quantity <= 0:
            cursor.execute('DELETE FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
        else:
            cursor.execute('UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?', 
                          (quantity, user_id, product_id))
        conn.commit()

def clear_cart(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        conn.commit()

def create_order(user_id, total_amount):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO orders (user_id, total_amount) VALUES (?, ?)', (user_id, total_amount))
        order_id = cursor.lastrowid
        conn.commit()
        return order_id

def add_order_item(order_id, product_id, quantity, price):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)', 
                      (order_id, product_id, quantity, price))
        conn.commit()

def get_order(order_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        return cursor.fetchone()

def get_order_items(order_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT oi.*, p.name, p.image, p.second_image, p.coordinates
            FROM order_items oi 
            JOIN products p ON oi.product_id = p.id 
            WHERE oi.order_id = ?
        ''', (order_id,))
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def update_order_status(order_id, status):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        conn.commit()

def add_discount(code, discount_type, value, min_order=None, max_uses=None, expires_at=None):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO discounts (code, discount_type, value, min_order, max_uses, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (code, discount_type, value, min_order, max_uses, expires_at))
        conn.commit()

def get_discount(code):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM discounts WHERE code = ?', (code,))
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None

def update_discount_usage(code):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE discounts SET used_count = used_count + 1 WHERE code = ?', (code,))
        conn.commit()

def get_all_discounts():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM discounts ORDER BY created_at DESC')
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def delete_discount(discount_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM discounts WHERE id = ?', (discount_id,))
        conn.commit()
