from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

engine = create_engine(config.DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price_eur = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    image1 = Column(String(500))
    image2 = Column(String(500))
    coordinates = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CryptoAddress(Base):
    __tablename__ = 'crypto_addresses'
    id = Column(Integer, primary_key=True)
    currency = Column(String(50), nullable=False)
    address = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    total_eur = Column(Float, nullable=False)
    total_usd = Column(Float, nullable=False)
    currency = Column(String(50))
    crypto_address = Column(String(255))
    source_address = Column(String(255))
    status = Column(String(50), default='pending')  # pending, confirmed, cancelled
    products = Column(JSON)  # List of product IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)

class DiscountCode(Base):
    __tablename__ = 'discount_codes'
    id = Column(Integer, primary_key=True)
    code = Column(String(100), nullable=False)
    discount_percent = Column(Float, nullable=False)
    user_id = Column(Integer)
    username = Column(String(100))
    is_active = Column(Boolean, default=True)
    used = Column(Boolean, default=False)

class CustomMessage(Base):
    __tablename__ = 'custom_messages'
    id = Column(Integer, primary_key=True)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)

class Statistics(Base):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True)
    visits = Column(Integer, default=0)
    orders_count = Column(Integer, default=0)
    revenue_eur = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)