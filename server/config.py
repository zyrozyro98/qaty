# -*- coding: utf-8 -*-
"""
إعدادات السيرفر
"""
import os
from datetime import timedelta

class Config:
    """إعدادات التطبيق"""
    # الأساسية
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj'
    API_KEY = 'rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj'
    
    # قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///qat_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=90)
    
    # CORS
    CORS_ORIGINS = ["*"]
    
    # ملفات التحميل
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # السماح بتحميل الصور
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # إعدادات البريد الإلكتروني
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@qat-app.com')
    
    # إعدادات الدفع
    PAYMENT_GATEWAY_URL = "https://api.payment-gateway.com/v1"
    PAYMENT_API_KEY = os.environ.get('PAYMENT_API_KEY', '')
    
    # إعدادات Firebase للإشعارات
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS', '')
    
    # إعدادات التطبيق
    APP_NAME = "تطبيق قات"
    APP_VERSION = "1.0.0"
    SUPPORT_PHONE = "771831482"
    SUPPORT_EMAIL = "support@qat-app.com"
    
    # أسعار الخدمات
    WASHING_PRICE = 100.0  # سعر غسل القات
    DELIVERY_FEE = 20.0   # رسوم التوصيل
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق"""
        # إنشاء مجلد التحميلات
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
        
        # إعدادات إضافية
        app.config['JSON_SORT_KEYS'] = False
        app.config['JSON_AS_ASCII'] = False
