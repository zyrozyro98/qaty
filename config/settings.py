# -*- coding: utf-8 -*-
"""
إعدادات التطبيق مع دعم Environment Variables
"""
import os
import json
import logging
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# مسار المجلد الأساسي
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """فئة الإعدادات الرئيسية"""
    
    # ========== الإعدادات الأساسية ==========
    SECRET_KEY = os.environ.get('SECRET_KEY', 'https://api.render.com/deploy/srv-d47p01e3jp1c73c5mb70?key=sdQH2xXNa_M')
    API_KEY = os.environ.get('API_KEY', 'rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj')
    
    APP_NAME = os.environ.get('APP_NAME', 'تطبيق قات')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    APP_ENV = os.environ.get('APP_ENV', 'development')
    
    # التصحيح
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    
    # ========== إعدادات قاعدة البيانات ==========
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///qat_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات تجمع الاتصالات
    SQLALCHEMY_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', 10))
    SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', 20))
    SQLALCHEMY_POOL_RECYCLE = int(os.environ.get('DB_POOL_RECYCLE', 3600))
    
    # ========== إعدادات JWT ==========
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    )
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    
    # ========== إعدادات البريد الإلكتروني ==========
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@qat-app.com')
    MAIL_DEBUG = os.environ.get('MAIL_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # ========== إعدادات الدفع ==========
    PAYMENT_GATEWAY_URL = os.environ.get('PAYMENT_GATEWAY_URL', 'https://api.paytabs.com/v2')
    PAYMENT_MERCHANT_EMAIL = os.environ.get('PAYMENT_MERCHANT_EMAIL')
    PAYMENT_SECRET_KEY = os.environ.get('PAYMENT_SECRET_KEY')
    PAYMENT_CURRENCY = os.environ.get('PAYMENT_CURRENCY', 'SAR')
    
    # محافظ إلكترونية
    JIB_WALLET_NUMBER = os.environ.get('JIB_WALLET_NUMBER', '771831482')
    JAWALY_WALLET_NUMBER = os.environ.get('JAWALY_WALLET_NUMBER', '771831482')
    MOBAIL_MONEY_NUMBER = os.environ.get('MOBAIL_MONEY_NUMBER', '771831482')
    SHAMEL_MONEY_NUMBER = os.environ.get('SHAMEL_MONEY_NUMBER', '771831482')
    FLOOSAK_WALLET_NUMBER = os.environ.get('FLOOSAK_WALLET_NUMBER', '771831482')
    
    # ========== إعدادات Firebase ==========
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL')
    
    # ========== إعدادات التخزين السحابي ==========
    # AWS S3
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_REGION = os.environ.get('AWS_REGION', 'me-south-1')
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    # ========== إعدادات التطبيق ==========
    # أسعار الخدمات
    WASHING_PRICE = float(os.environ.get('WASHING_PRICE', 100))
    DELIVERY_FEE = float(os.environ.get('DELIVERY_FEE', 20))
    TAX_PERCENTAGE = float(os.environ.get('TAX_PERCENTAGE', 15))
    
    # أوقات العمل
    WORK_START_TIME = os.environ.get('WORK_START_TIME', '09:00')
    WORK_END_TIME = os.environ.get('WORK_END_TIME', '22:00')
    WORK_DAYS = [int(day) for day in os.environ.get('WORK_DAYS', '0,1,2,3,4').split(',')]
    
    # إعدادات التطبيق
    APP_LANGUAGE = os.environ.get('APP_LANGUAGE', 'ar')
    APP_TIMEZONE = os.environ.get('APP_TIMEZONE', 'Asia/Riyadh')
    APP_CURRENCY = os.environ.get('APP_CURRENCY', 'ريال')
    APP_COUNTRY = os.environ.get('APP_COUNTRY', 'SA')
    
    # ========== إعدادات الأمان ==========
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5000,http://localhost:8080').split(',')
    CORS_METHODS = os.environ.get('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(',')
    CORS_HEADERS = os.environ.get('CORS_HEADERS', 'Content-Type,Authorization,X-API-Key').split(',')
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT = int(os.environ.get('RATE_LIMIT_DEFAULT', 100))
    RATE_LIMIT_AUTH = int(os.environ.get('RATE_LIMIT_AUTH', 10))
    
    # SSL/HTTPS
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH', 'ssl/cert.pem')
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', 'ssl/key.pem')
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'False').lower() in ('true', '1', 't')
    
    # ========== إعدادات التحليلات ==========
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
    MIXPANEL_TOKEN = os.environ.get('MIXPANEL_TOKEN')
    
    # ========== إعدادات الدعم ==========
    SUPPORT_PHONE = os.environ.get('SUPPORT_PHONE', '771831482')
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'support@qat-app.com')
    SUPPORT_WHATSAPP = os.environ.get('SUPPORT_WHATSAPP', '771831482')
    SUPPORT_TELEGRAM = os.environ.get('SUPPORT_TELEGRAM', '@qat_app_support')
    
    # معلومات الحساب البنكي
    BANK_ACCOUNT_NAME = os.environ.get('BANK_ACCOUNT_NAME', 'يوسف محمد علي حمود زهير')
    BANK_ACCOUNT_NUMBER = os.environ.get('BANK_ACCOUNT_NUMBER', 'SA1234567890123456789012')
    BANK_NAME = os.environ.get('BANK_NAME', 'البنك الأهلي التجاري')
    BANK_BRANCH = os.environ.get('BANK_BRANCH', 'فرع الرياض')
    
    # ========== إعدادات الإعلانات ==========
    ADMOB_APP_ID = os.environ.get('ADMOB_APP_ID', 'ca-app-pub-3940256099942544~3347511713')
    ADMOB_BANNER_ID = os.environ.get('ADMOB_BANNER_ID', 'ca-app-pub-3940256099942544/6300978111')
    ADMOB_INTERSTITIAL_ID = os.environ.get('ADMOB_INTERSTITIAL_ID', 'ca-app-pub-3940256099942544/1033173712')
    
    # ========== إعدادات السجل ==========
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', str(BASE_DIR / 'logs' / 'app.log'))
    LOG_MAX_SIZE = int(os.environ.get('LOG_MAX_SIZE', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # ========== إعدادات اختبار API ==========
    TEST_MODE = os.environ.get('TEST_MODE', 'False').lower() in ('true', '1', 't')
    TEST_PHONE = os.environ.get('TEST_PHONE', '771234567')
    TEST_EMAIL = os.environ.get('TEST_EMAIL', 'test@qat-app.com')
    TEST_PASSWORD = os.environ.get('TEST_PASSWORD', '123456')
    
    # ========== إعدادات الملفات ==========
    # مجلدات التحميل
    UPLOAD_FOLDER = str(BASE_DIR / 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # الامتدادات المسموح بها
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # ========== إعدادات الأداء ==========
    # التخزين المؤقت
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 دقائق
    
    # ضغط الاستجابة
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml', 
        'application/json', 'application/javascript'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    
    @classmethod
    def init_app(cls, app):
        """تهيئة التطبيق مع الإعدادات"""
        # إعداد السجل
        cls.setup_logging()
        
        # إنشاء المجلدات المطلوبة
        cls.create_directories()
        
        # إعدادات إضافية
        app.config['JSON_SORT_KEYS'] = False
        app.config['JSON_AS_ASCII'] = False
        
        # تحميل إعدادات Firebase إذا كانت موجودة
        if cls.FIREBASE_CREDENTIALS_PATH and os.path.exists(cls.FIREBASE_CREDENTIALS_PATH):
            import firebase_admin
            from firebase_admin import credentials
            
            cred = credentials.Certificate(cls.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': cls.FIREBASE_DATABASE_URL
            })
    
    @classmethod
    def setup_logging(cls):
        """إعداد نظام السجل"""
        # إنشاء مجلد السجلات
        log_dir = os.path.dirname(cls.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # تهيئة السجل
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    @classmethod
    def create_directories(cls):
        """إنشاء المجلدات المطلوبة"""
        directories = [
            cls.UPLOAD_FOLDER,
            os.path.dirname(cls.LOG_FILE),
            BASE_DIR / 'ssl',
            BASE_DIR / 'static',
            BASE_DIR / 'templates'
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    @classmethod
    def get_wallet_info(cls):
        """الحصول على معلومات المحافظ الإلكترونية"""
        return {
            'jib': {
                'name': 'محفظة جيب',
                'number': cls.JIB_WALLET_NUMBER,
                'owner': cls.BANK_ACCOUNT_NAME
            },
            'jawaly': {
                'name': 'محفظة جوالي',
                'number': cls.JAWALY_WALLET_NUMBER,
                'owner': cls.BANK_ACCOUNT_NAME
            },
            'mobail_money': {
                'name': 'محفظة موبايل موني',
                'number': cls.MOBAIL_MONEY_NUMBER,
                'owner': cls.BANK_ACCOUNT_NAME
            },
            'shamel_money': {
                'name': 'محفظة الشامل موني',
                'number': cls.SHAMEL_MONEY_NUMBER,
                'owner': cls.BANK_ACCOUNT_NAME
            },
            'floosak': {
                'name': 'محفظة فلوسك',
                'number': cls.FLOOSAK_WALLET_NUMBER,
                'owner': cls.BANK_ACCOUNT_NAME
            }
        }
    
    @classmethod
    def get_bank_info(cls):
        """الحصول على معلومات الحساب البنكي"""
        return {
            'account_name': cls.BANK_ACCOUNT_NAME,
            'account_number': cls.BANK_ACCOUNT_NUMBER,
            'bank_name': cls.BANK_NAME,
            'branch': cls.BANK_BRANCH,
            'phone': cls.SUPPORT_PHONE
        }
    
    @classmethod
    def get_support_info(cls):
        """الحصول على معلومات الدعم"""
        return {
            'phone': cls.SUPPORT_PHONE,
            'email': cls.SUPPORT_EMAIL,
            'whatsapp': cls.SUPPORT_WHATSAPP,
            'telegram': cls.SUPPORT_TELEGRAM
        }


# إعدادات التطوير
class DevelopmentConfig(Config):
    """إعدادات التطوير"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_qat_app.db'
    LOG_LEVEL = 'DEBUG'


# إعدادات الاختبار
class TestingConfig(Config):
    """إعدادات الاختبار"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_qat_app.db'
    LOG_LEVEL = 'DEBUG'
    TEST_MODE = True


# إعدادات الإنتاج
class ProductionConfig(Config):
    """إعدادات الإنتاج"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    FORCE_HTTPS = True
    
    # إعدادات قاعدة بيانات الإنتاج
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    
    # إعدادات البريد في الإنتاج
    MAIL_DEBUG = False


# اختيار التكوين المناسب
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """الحصول على التكوين المناسب"""
    if config_name is None:
        config_name = os.environ.get('APP_ENV', 'default')
    
    config_class = config_dict.get(config_name, config_dict['default'])
    return config_class()
