# -*- coding: utf-8 -*-
"""
حزمة السيرفر الرئيسية
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

# إنشاء كائنات التمديدات
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=None):
    """إنشاء وتكوين تطبيق Flask"""
    app = Flask(__name__)
    
    # تحميل الإعدادات
    if config_class:
        app.config.from_object(config_class)
    else:
        # الإعدادات الافتراضية
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///qat_app.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 ساعة
        
        # إعدادات التحميل
        app.config['UPLOAD_FOLDER'] = 'uploads'
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    # تهيئة التمديدات
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # تسجيل النماذج
    from app.database import models
    
    # تسجيل البلوبوينتس
    from server.routes.auth import auth_bp
    from server.routes.products import products_bp
    from server.routes.orders import orders_bp
    from server.routes.payments import payments_bp
    from server.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)
    
    # إنشاء الجداول
    with app.app_context():
        db.create_all()
    
    # تسجيل معالجات الأخطاء
    @app.errorhandler(404)
    def not_found_error(error):
        return {'success': False, 'message': 'الصفحة غير موجودة'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'success': False, 'message': 'خطأ داخلي في السيرفر'}, 500
    
    return app
