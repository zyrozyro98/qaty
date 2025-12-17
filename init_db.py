#!/usr/bin/env python3
"""
سكريبت لتهيئة قاعدة البيانات وإضافة البيانات الأساسية
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Wallet, Market, WashingStation
from werkzeug.security import generate_password_hash

def init_database():
    with app.app_context():
        print("🚀 بدء تهيئة قاعدة البيانات...")
        
        # إنشاء جميع الجداول
        db.create_all()
        print("✅ تم إنشاء الجداول")
        
        # إنشاء حساب المدير إذا لم يكن موجوداً
        admin = User.query.filter_by(user_type='admin').first()
        if not admin:
            admin = User(
                name="مدير النظام",
                phone="771831482",
                email="admin@qaty.com",
                password=generate_password_hash("Admin@123"),
                user_type="admin"
            )
            db.session.add(admin)
            db.session.commit()
            
            # إنشاء محفظة للمدير
            wallet = Wallet(user_id=admin.id, balance=10000.0)
            db.session.add(wallet)
            db.session.commit()
            
            print("✅ تم إنشاء حساب المدير")
            print(f"   البريد: admin@qaty.com")
            print(f"   كلمة المرور: Admin@123")
        
        # إنشاء أسواق افتراضية
        markets_data = [
            {"name": "سوق التحرير", "location": "صنعاء", "city": "صنعاء"},
            {"name": "سوق الخضرة", "location": "صنعاء", "city": "صنعاء"},
            {"name": "سوق الصالح", "location": "تعز", "city": "تعز"},
            {"name": "سوق الثورة", "location": "عدن", "city": "عدن"}
        ]
        
        for market_data in markets_data:
            market = Market.query.filter_by(name=market_data["name"]).first()
            if not market:
                market = Market(**market_data)
                db.session.add(market)
                db.session.commit()
                
                # إنشاء محطة غسيل لكل سوق
                washing_station = WashingStation(
                    name=f"محطة غسيل {market_data['name']}",
                    market_id=market.id,
                    phone="771831482",
                    washing_price=100.0,
                    is_active=True
                )
                db.session.add(washing_station)
        
        db.session.commit()
        print("✅ تم إنشاء الأسواق ومحطات الغسيل")
        
        print("\n🎉 تم تهيئة قاعدة البيانات بنجاح!")

if __name__ == "__main__":
    init_database()
