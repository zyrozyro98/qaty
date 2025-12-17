#!/usr/bin/env python3
"""
تهيئة قاعدة البيانات لـ Render
"""
import os
import sys
import traceback

print("🔧 بدء تهيئة قاعدة البيانات على Render...")
print(f"📁 المسار الحالي: {os.getcwd()}")
print(f"🐍 إصدار Python: {sys.version}")

# إضافة المسار
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from __init__ import create_app, db
    from models import User, Market
    import hashlib
    
    print("✅ تم استيراد المكتبات بنجاح")
    
    # إنشاء التطبيق
    app = create_app()
    
    with app.app_context():
        print("🔨 إنشاء الجداول...")
        db.create_all()
        print("✅ تم إنشاء الجداول")
        
        # التحقق من وجود المدير
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("👨‍💼 إنشاء حساب المدير...")
            # إنشاء حساب المدير
            admin = User(
                username='admin',
                password=hashlib.sha256('admin123'.encode()).hexdigest(),
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
        print("🏪 إنشاء الأسواق الافتراضية...")
        markets_data = [
            ('سوق تعز', 'وسط المدينة', 'تعز'),
            ('سوق صنعاء', 'شارع الزبيري', 'صنعاء'),
            ('سوق الحديدة', 'الميناء', 'الحديدة'),
            ('سوق إب', 'وسط المحافظة', 'إب')
        ]
        
        markets_created = 0
        for name, location, city in markets_data:
            market = Market.query.filter_by(name=name).first()
            if not market:
                market = Market(name=name, location=location, city=city)
                db.session.add(market)
                markets_created += 1
        
        db.session.commit()
        print(f"✅ تم إنشاء {markets_created} سوق")
        
        # إنشاء مستخدمين تجريبيين
        print("👥 إنشاء المستخدمين التجريبيين...")
        
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
                user = User(
                    username=user_data['username'],
                    password=hashlib.sha256(user_data['password'].encode()).hexdigest(),
                    full_name=user_data['full_name'],
                    email=user_data['email'],
                    phone=user_data['phone'],
                    role=user_data['role'],
                    store_name=user_data.get('store_name', ''),
                    vehicle_type=user_data.get('vehicle_type', ''),
                    wallet_balance=user_data.get('wallet_balance', 0.0),
                    is_active=True
                )
                db.session.add(user)
                users_created += 1
        
        db.session.commit()
        print(f"✅ تم إنشاء {users_created} مستخدم تجريبي")
        
        print("\n" + "="*50)
        print("🎉 تم تهيئة قاعدة البيانات بنجاح!")
        print("="*50)
        print("\n📋 معلومات النظام:")
        print("-"*30)
        print(f"👤 إجمالي المستخدمين: {User.query.count()}")
        print(f"🏪 إجمالي الأسواق: {Market.query.count()}")
        print("-"*30)
        print("\n🔧 معلومات الدخول:")
        print("-"*30)
        print("👨‍💼 المدير: admin / admin123")
        print("👨‍🌾 البائع: seller1 / 123456")
        print("👨‍💼 المشتري: buyer1 / 123456")
        print("🚚 مندوب التوصيل: driver1 / 123456")
        print("-"*30)
        print(f"\n📞 الدعم: 771831482")
        print(f"🔑 API Key: rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj")
        print("="*50)
        
except Exception as e:
    print(f"❌ خطأ في تهيئة قاعدة البيانات: {str(e)}")
    print("\n🔍 تفاصيل الخطأ:")
    traceback.print_exc()
    sys.exit(1)
