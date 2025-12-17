# -*- coding: utf-8 -*-
"""
تشغيل سيرفر API
"""
import os
from server import create_app
from server.config import Config

app = create_app(Config)

if __name__ == '__main__':
    # إنشاء مجلد التحميلات
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    # تشغيل السيرفر
    print("🚀 تشغيل سيرفر تطبيق قات...")
    print(f"📊 API Key: {Config.API_KEY}")
    print(f"🔗 العنوان: http://localhost:5000")
    print(f"📁 قاعدة البيانات: {Config.SQLALCHEMY_DATABASE_URI}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
