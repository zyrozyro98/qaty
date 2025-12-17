#!/usr/bin/env python3
"""
تهيئة قاعدة البيانات لـ Render
"""
import os
import sys
from pathlib import Path

# إضافة المسار
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔧 بدء تهيئة قاعدة البيانات...")

try:
    from app import create_app, db
    from app.config import Config
    from app.models import User
    
    # إنشاء التطبيق
    app = create_app(Config)
    
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        print("✅ تم إنشاء الجداول")
        
        # التحقق من وجود المدير
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            # إنشاء حساب المدير
            admin = User(
                username='admin',
                password='admin123',
                full_name='المدير العام',
                email='admin@qat-app.com',
                phone='771831482',
                role='admin',
                wallet_balance=10000.0,
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ تم إنشاء حساب المدير")
        else:
            print("ℹ️ حساب المدير موجود بالفعل")
        
        print("\n🎉 تم تهيئة قاعدة البيانات بنجاح!")
        print("\n📋 معلومات الدخول:")
        print("-" * 30)
        print(f"🔗 عنوان API: https://qat-api.onrender.com")
        print(f"🔑 API Key: {Config.API_KEY}")
        print(f"📞 الدعم: {Config.SUPPORT_PHONE}")
        print(f"👨‍💼 المدير: admin / admin123")
        print("-" * 30)
        
except Exception as e:
    print(f"❌ خطأ في تهيئة قاعدة البيانات: {str(e)}")
    sys.exit(1)
