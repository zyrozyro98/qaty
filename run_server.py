#!/usr/bin/env python3
"""
تشغيل سيرفر API
"""
import os
from app import create_app
from app.config import Config

# إنشاء التطبيق
app = create_app(Config)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("\n" + "="*60)
    print("🚀 تشغيل سيرفر تطبيق قات API")
    print("="*60)
    print(f"📦 التطبيق: {Config.APP_NAME} v{Config.APP_VERSION}")
    print(f"🌐 العنوان: http://0.0.0.0:{port}")
    print(f"🔧 الوضع: {'تطوير' if debug else 'إنتاج'}")
    print(f"📊 قاعدة البيانات: {Config.SQLALCHEMY_DATABASE_URI[:30]}...")
    print(f"🔑 API Key: {Config.API_KEY}")
    print(f"📞 الدعم: {Config.SUPPORT_PHONE}")
    print("="*60)
    print("\n📡 نقاط النهاية المتاحة:")
    print("-"*40)
    print("GET  /              - الصفحة الرئيسية")
    print("GET  /health        - فحص الصحة")
    print("POST /api/auth/login - تسجيل الدخول")
    print("POST /api/auth/register - تسجيل جديد")
    print("GET  /api/products  - جلب المنتجات")
    print("POST /api/orders    - إنشاء طلب")
    print("-"*40)
    print("\n👤 معلومات الدخول:")
    print("-"*40)
    print("المدير: admin / admin123")
    print("البائع: seller1 / 123456")
    print("المشتري: buyer1 / 123456")
    print("مندوب التوصيل: driver1 / 123456")
    print("="*60)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
