"""
نماذج قاعدة البيانات
"""
from datetime import datetime
from __init__ import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, seller, buyer, driver
    wallet_balance = db.Column(db.Float, default=0.0)
    store_name = db.Column(db.String(100))
    vehicle_type = db.Column(db.String(50))
    rating = db.Column(db.Float, default=5.0)
    total_ratings = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    seller = db.relationship('User', backref='products')
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(20), unique=True, nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    washing_price = db.Column(db.Float, default=0.0)
    final_price = db.Column(db.Float, nullable=False)
    washing_required = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_notes = db.Column(db.Text)
    estimated_delivery = db.Column(db.DateTime)
    actual_delivery = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    buyer = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])
    product = db.relationship('Product', foreign_keys=[product_id])
    
    def __repr__(self):
        return f'<Order {self.order_code}>'

class Market(db.Model):
    __tablename__ = 'markets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Market {self.name}>'
