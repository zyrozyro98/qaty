# -*- coding: utf-8 -*-
"""
نماذج قاعدة البيانات - SQLAlchemy
"""
from datetime import datetime
from app.database import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, seller, buyer, driver, washer
    wallet_balance = db.Column(db.Float, default=0.0)
    store_name = db.Column(db.String(100))
    vehicle_type = db.Column(db.String(50))
    rating = db.Column(db.Float, default=5.0)
    total_ratings = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    products = db.relationship('Product', backref='seller', lazy=True)
    orders_as_buyer = db.relationship('Order', foreign_keys='Order.buyer_id', backref='buyer', lazy=True)
    orders_as_seller = db.relationship('Order', foreign_keys='Order.seller_id', backref='seller_obj', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'wallet_balance': self.wallet_balance,
            'store_name': self.store_name,
            'vehicle_type': self.vehicle_type,
            'rating': self.rating,
            'total_ratings': self.total_ratings,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

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
    
    # العلاقات
    washers = db.relationship('QatWasher', backref='market', lazy=True)
    products = db.relationship('Product', backref='market_obj', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'city': self.city,
            'lat': self.lat,
            'lng': self.lng,
            'is_active': self.is_active
        }

class QatWasher(db.Model):
    __tablename__ = 'qat_washers'
    
    id = db.Column(db.Integer, primary_key=True)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    owner_name = db.Column(db.String(100))
    price_per_wash = db.Column(db.Float, default=100.0)
    is_available = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=5.0)
    total_orders = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'market_id': self.market_id,
            'name': self.name,
            'phone': self.phone,
            'owner_name': self.owner_name,
            'price_per_wash': self.price_per_wash,
            'is_available': self.is_available,
            'rating': self.rating,
            'total_orders': self.total_orders
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # صعدي, همداني, أرحبي, etc.
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    orders = db.relationship('Order', backref='product_obj', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'quantity': self.quantity,
            'image_url': self.image_url,
            'rating': self.rating,
            'total_reviews': self.total_reviews,
            'is_available': self.is_available,
            'market_id': self.market_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

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
    washer_id = db.Column(db.Integer, db.ForeignKey('qat_washers.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, washing, dispatched, delivered, cancelled
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_notes = db.Column(db.Text)
    estimated_delivery = db.Column(db.DateTime)
    actual_delivery = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات الإضافية
    seller = db.relationship('User', foreign_keys=[seller_id])
    product = db.relationship('Product', foreign_keys=[product_id])
    washer = db.relationship('QatWasher', foreign_keys=[washer_id])
    driver = db.relationship('User', foreign_keys=[driver_id])
    market = db.relationship('Market', foreign_keys=[market_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_code': self.order_code,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'washing_price': self.washing_price,
            'final_price': self.final_price,
            'washing_required': self.washing_required,
            'washer_id': self.washer_id,
            'driver_id': self.driver_id,
            'market_id': self.market_id,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'delivery_address': self.delivery_address,
            'delivery_notes': self.delivery_notes,
            'estimated_delivery': self.estimated_delivery.isoformat() if self.estimated_delivery else None,
            'actual_delivery': self.actual_delivery.isoformat() if self.actual_delivery else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'seller_name': self.seller.full_name if self.seller else None,
            'product_name': self.product.name if self.product else None
        }

class Advertisement(db.Model):
    __tablename__ = 'advertisements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    target_url = db.Column(db.String(500))
    advertiser_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ad_package_id = db.Column(db.Integer, db.ForeignKey('ad_packages.id'))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'views': self.views,
            'clicks': self.clicks,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }

class AdPackage(db.Model):
    __tablename__ = 'ad_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_days = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_impressions = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration_days': self.duration_days,
            'price': self.price,
            'max_impressions': self.max_impressions,
            'is_active': self.is_active
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # order_placed, order_confirmed, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON)  # بيانات إضافية JSON
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Withdrawal(db.Model):
    __tablename__ = 'withdrawals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    wallet_type = db.Column(db.String(50), nullable=False)  # jib, jawaly, etc.
    wallet_number = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    admin_notes = db.Column(db.Text)
    processed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'wallet_type': self.wallet_type,
            'wallet_number': self.wallet_number,
            'full_name': self.full_name,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    rated_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rater_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating_value = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    type = db.Column(db.String(20))  # product, seller, driver, washer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', foreign_keys=[order_id])
    rated_user = db.relationship('User', foreign_keys=[rated_user_id])
    rater_user = db.relationship('User', foreign_keys=[rater_user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'rated_user_id': self.rated_user_id,
            'rater_user_id': self.rater_user_id,
            'rating_value': self.rating_value,
            'comment': self.comment,
            'type': self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class GiftCode(db.Model):
    __tablename__ = 'gift_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    used_at = db.Column(db.DateTime)
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    creator = db.relationship('User', foreign_keys=[created_by])
    user = db.relationship('User', foreign_keys=[used_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'amount': self.amount,
            'is_used': self.is_used,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
