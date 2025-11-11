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

# ... (muud funktsioonid jäävad samaks nagu sinu praeguses failis)
