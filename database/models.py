from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # admin, seller, buyer, driver, washing_manager
    store_name = db.Column(db.String(100))
    vehicle_type = db.Column(db.String(50))
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    products = db.relationship('Product', backref='seller', lazy=True)
    orders_as_buyer = db.relationship('Order', foreign_keys='Order.buyer_id', backref='buyer', lazy=True)
    orders_as_seller = db.relationship('Order', foreign_keys='Order.seller_id', backref='seller', lazy=True)
    wallet = db.relationship('Wallet', backref='user', uselist=False, lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'user_type': self.user_type,
            'store_name': self.store_name,
            'vehicle_type': self.vehicle_type,
            'rating': self.rating,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))  # صعدي, همداني, أرحبي, إلخ
    quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'))
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    market = db.relationship('Market', backref='products')
    reviews = db.relationship('Review', backref='product', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'quantity': self.quantity,
            'image_url': self.image_url,
            'seller_id': self.seller_id,
            'seller_name': self.seller.name if self.seller else None,
            'market_id': self.market_id,
            'market_name': self.market.name if self.market else None,
            'rating': self.rating,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(20), unique=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    washing_price = db.Column(db.Float, default=0)  # تكلفة الغسيل
    total_price = db.Column(db.Float, nullable=False)
    requires_washing = db.Column(db.Boolean, default=False)
    sale_code = db.Column(db.String(20), unique=True)
    delivery_address = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, washing, delivering, delivered, cancelled
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed
    washing_station_id = db.Column(db.Integer, db.ForeignKey('washing_stations.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    estimated_delivery = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    product = db.relationship('Product', backref='orders')
    washing_station = db.relationship('WashingStation', backref='orders')
    driver = db.relationship('User', foreign_keys=[driver_id], backref='deliveries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_code': self.order_code,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'washing_price': self.washing_price,
            'total_price': self.total_price,
            'requires_washing': self.requires_washing,
            'sale_code': self.sale_code,
            'delivery_address': self.delivery_address,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'washing_station_id': self.washing_station_id,
            'driver_id': self.driver_id,
            'driver_name': self.driver.name if self.driver else None,
            'estimated_delivery': self.estimated_delivery.isoformat() if self.estimated_delivery else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'created_at': self.created_at.isoformat()
        }

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    jib_wallet = db.Column(db.String(20))
    jawaly_wallet = db.Column(db.String(20))
    mobile_money_wallet = db.Column(db.String(20))
    shamel_money_wallet = db.Column(db.String(20))
    fulusik_wallet = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'balance': self.balance,
            'jib_wallet': self.jib_wallet,
            'jawaly_wallet': self.jawaly_wallet,
            'mobile_money_wallet': self.mobile_money_wallet,
            'shamel_money_wallet': self.shamel_money_wallet,
            'fulusik_wallet': self.fulusik_wallet,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # deposit, withdrawal, purchase, sale, refund
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    reference_number = db.Column(db.String(100), unique=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='transactions')
    order = db.relationship('Order', backref='transactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'payment_method': self.payment_method,
            'status': self.status,
            'reference_number': self.reference_number,
            'order_id': self.order_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class Market(db.Model):
    __tablename__ = 'markets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    city = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'city': self.city,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class WashingStation(db.Model):
    __tablename__ = 'washing_stations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    phone = db.Column(db.String(20))
    washing_price = db.Column(db.Float, default=100.0)  # سعر الغسيل الافتراضي
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    market = db.relationship('Market', backref='washing_stations')
    manager = db.relationship('User', backref='managed_washing_stations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'market_id': self.market_id,
            'market_name': self.market.name if self.market else None,
            'manager_id': self.manager_id,
            'manager_name': self.manager.name if self.manager else None,
            'phone': self.phone,
            'washing_price': self.washing_price,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', foreign_keys=[user_id], backref='reviews_given')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='reviews_received')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'product_id': self.product_id,
            'seller_id': self.seller_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

class Advertisement(db.Model):
    __tablename__ = 'advertisements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    target_url = db.Column(db.String(500))
    ad_type = db.Column(db.String(50))  # banner, popup, interstitial
    position = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'target_url': self.target_url,
            'ad_type': self.ad_type,
            'position': self.position,
            'is_active': self.is_active,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat()
        }

class AdPackage(db.Model):
    __tablename__ = 'ad_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    max_impressions = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration_days': self.duration_days,
            'max_impressions': self.max_impressions,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # order, payment, system, promotion
    is_read = db.Column(db.Boolean, default=False)
    data = db.Column(db.JSON)  # بيانات إضافية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'data': self.data,
            'created_at': self.created_at.isoformat()
        }
