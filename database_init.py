# -*- coding: utf-8 -*-
"""
تهيئة قاعدة البيانات ببيانات أولية
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import create_app, db
from server.config import Config
from app.database.models import *

def init_database():
    """تهيئة قاعدة البيانات"""
    app = create_app(Config)
    
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # التحقق من وجود المدير
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            # إنشاء مدير النظام
            admin = User(
                username='admin',
                password='admin123',  # في التطبيق الحقيقي، يجب تشفير كلمة المرور
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
        
        # إنشاء أسواق افتراضية
        default_markets = [
            {
                'name': 'سوق تعز',
                'location': 'وسط المدينة',
                'city': 'تعز',
                'lat': 13.5789,
                'lng': 44.0219
            },
            {
                'name': 'سوق صنعاء',
                'location': 'شارع الزبيري',
                'city': 'صنعاء',
                'lat': 15.3694,
                'lng': 44.1910
            },
            {
                'name': 'سوق الحديدة',
                'location': 'الميناء',
                'city': 'الحديدة',
                'lat': 14.8022,
                'lng': 42.9545
            },
            {
                'name': 'سوق إب',
                'location': 'وسط المحافظة',
                'city': 'إب',
                'lat': 13.9667,
                'lng': 44.1833
            }
        ]
        
        markets_created = 0
        for market_data in default_markets:
            market = Market.query.filter_by(name=market_data['name']).first()
            if not market:
                market = Market(**market_data)
                db.session.add(market)
                markets_created += 1
        
        db.session.commit()
        print(f"✅ تم إنشاء {markets_created} سوق")
        
        # إنشاء مغاسل افتراضية
        markets = Market.query.all()
        washers_created = 0
        
        for market in markets:
            washer = QatWasher.query.filter_by(market_id=market.id).first()
            if not washer:
                washer = QatWasher(
                    market_id=market.id,
                    name=f'مغسلة {market.name}',
                    phone='771234567',
                    owner_name='مدير المغسلة',
                    price_per_wash=100.0,
                    is_available=True
                )
                db.session.add(washer)
                washers_created += 1
        
        db.session.commit()
        print(f"✅ تم إنشاء {washers_created} مغسلة")
        
        # إنشاء باقات إعلانات افتراضية
        default_packages = [
            {
                'name': 'الباقة الأساسية',
                'description': 'إعلان لمدة 7 أيام يظهر في التطبيق',
                'duration_days': 7,
                'price': 50.0,
                'max_impressions': 1000
            },
            {
                'name': 'الباقة المتوسطة',
                'description': 'إعلان مميز لمدة 30 يوماً',
                'duration_days': 30,
                'price': 200.0,
                'max_impressions': 5000
            },
            {
                'name': 'الباقة المميزة',
                'description': 'إعلان في الصفحة الرئيسية لمدة 60 يوماً',
                'duration_days': 60,
                'price': 500.0,
                'max_impressions': 15000
            }
        ]
        
        packages_created = 0
        for package_data in default_packages:
            package = AdPackage.query.filter_by(name=package_data['name']).first()
            if not package:
                package = AdPackage(**package_data)
                db.session.add(package)
                packages_created += 1
        
        db.session.commit()
        print(f"✅ تم إنشاء {packages_created} باقة إعلانية")
        
        # إنشاء مستخدمين تجريبيين
        demo_users = [
            {
                'username': 'seller1',
                'password': '123456',
                'full_name': 'بائع تجريبي ١',
                'email': 'seller1@qat-app.com',
                'phone': '771000001',
                'role': 'seller',
                'store_name': 'متجر القات الأول',
                'wallet_balance': 5000.0
            },
            {
                'username': 'buyer1',
                'password': '123456',
                'full_name': 'مشتري تجريبي ١',
                'email': 'buyer1@qat-app.com',
                'phone': '771000002',
                'role': 'buyer',
                'wallet_balance': 1000.0
            },
            {
                'username': 'driver1',
                'password': '123456',
                'full_name': 'مندوب توصيل ١',
                'email': 'driver1@qat-app.com',
                'phone': '771000003',
                'role': 'driver',
                'vehicle_type': 'دراجة نارية',
                'wallet_balance': 500.0
            }
        ]
        
        users_created = 0
        for user_data in demo_users:
            user = User.query.filter_by(username=user_data['username']).first()
            if not user:
                user = User(**user_data)
                db.session.add(user)
                users_created += 1
        
        db.session.commit()
        print(f"✅ تم إنشاء {users_created} مستخدم تجريبي")
        
        print("\n🎉 تم تهيئة قاعدة البيانات بنجاح!")
        print("\n📋 معلومات الدخول:")
        print("المدير: admin / admin123")
        print("البائع: seller1 / 123456")
        print("المشتري: buyer1 / 123456")
        print("مندوب التوصيل: driver1 / 123456")
        print(f"\n🔑 API Key: {Config.API_KEY}")
        print("📞 الدعم: 771831482")

if __name__ == '__main__':
    init_database()
