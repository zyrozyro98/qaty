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

def create_app():
    """إنشاء وتكوين تطبيق Flask"""
    app = Flask(__name__)
    
    # الإعدادات الأساسية
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj')
    app.config['API_KEY'] = os.environ.get('API_KEY', 'rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///qat_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    
    # تهيئة التمديدات
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # تسجيل النماذج
    import models
    
    # تسجيل المسارات
    from routes import auth, products, orders, admin
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(products.bp, url_prefix='/api/products')
    app.register_blueprint(orders.bp, url_prefix='/api/orders')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    
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
        try:
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except:
            db_status = 'disconnected'
            
        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': db_status,
            'timestamp': '2024-01-01T00:00:00Z'
        })
    
    return app
