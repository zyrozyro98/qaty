"""
حزمة التطبيق الرئيسية
"""
from flask import Flask, jsonify
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
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # تسجيل النماذج
    from app import models
    
    # تسجيل البلوبوينتس
    from app.routes import auth, products, orders, admin
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(admin.bp)
    
    @app.route('/')
    def index():
        return jsonify({
            'success': True,
            'message': 'مرحباً بك في API تطبيق قات',
            'version': '1.0.0',
            'support': '771831482',
            'endpoints': {
                'auth': '/api/auth',
                'products': '/api/products',
                'orders': '/api/orders',
                'admin': '/api/admin'
            }
        })
    
    @app.route('/health')
    def health():
        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': 'connected' if db.session.connection() else 'disconnected'
        })
    
    # إنشاء الجداول في سياق التطبيق
    with app.app_context():
        try:
            db.create_all()
            print("✅ تم إنشاء/تأكيد الجداول")
        except Exception as e:
            print(f"⚠️  ملاحظة: {str(e)}")
    
    return app
