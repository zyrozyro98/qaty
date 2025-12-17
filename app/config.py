"""
إعدادات التطبيق
"""
import os
from datetime import timedelta

class Config:
    """إعدادات التطبيق"""
    
    # ========== الإعدادات الأساسية ==========
    SECRET_KEY = os.environ.get('SECRET_KEY', 'rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj')
    API_KEY = os.environ.get('API_KEY', 'rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj')
    
    APP_NAME = "تطبيق قات"
    APP_VERSION = "1.0.0"
    APP_ENV = os.environ.get('APP_ENV', 'production')
    
    # التصحيح
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    
    # ========== إعدادات قاعدة البيانات ==========
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///qat_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ========== إعدادات JWT ==========
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # ========== إعدادات التطبيق ==========
    WASHING_PRICE = 100.0
    DELIVERY_FEE = 20.0
    
    # ========== إعدادات الدعم ==========
    SUPPORT_PHONE = os.environ.get('SUPPORT_PHONE', '771831482')
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'support@qat-app.com')
    
    # محافظ إلكترونية
    JIB_WALLET_NUMBER = SUPPORT_PHONE
    JAWALY_WALLET_NUMBER = SUPPORT_PHONE
    MOBAIL_MONEY_NUMBER = SUPPORT_PHONE
    SHAMEL_MONEY_NUMBER = SUPPORT_PHONE
    FLOOSAK_WALLET_NUMBER = SUPPORT_PHONE
    
    # معلومات الحساب البنكي
    BANK_ACCOUNT_NAME = "يوسف محمد علي حمود زهير"
    BANK_ACCOUNT_NUMBER = "SA1234567890123456789012"
    BANK_NAME = "البنك الأهلي التجاري"
    
    # ========== إعدادات CORS ==========
    CORS_ORIGINS = ["*"]
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق"""
        pass
