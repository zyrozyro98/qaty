"""
حزمة التطبيق الرئيسية
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os

# إنشاء كائنات التمديدات
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class):
    """إنشاء وتكوين تطبيق Flask"""
    app = Flask(__name__)
    
    # تحميل الإعدادات
    app.config.from_object(config_class)
    
    # تهيئة التمديدات
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # تسجيل النماذج (مهم للـ migrations)
    from app import models
    
    # تسجيل البلوبوينتس
    from app.routes import auth, products, orders, admin
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(products.bp, url_prefix='/api/products')
    app.register_blueprint(orders.bp, url_prefix='/api/orders')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    
    # إنشاء الجداول
    with app.app_context():
        db.create_all()
    
    return app
