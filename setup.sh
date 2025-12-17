#!/bin/bash

# سكريبت إعداد سريع
echo "🔧 إعداد تطبيق قات لـ Render..."

# تحديث pip
pip install --upgrade pip

# تثبيت المتطلبات
pip install -r requirements.txt

# تهيئة قاعدة البيانات
echo "🗄️  تهيئة قاعدة البيانات..."
python database_init.py

echo "✅ تم الإعداد بنجاح!"
echo ""
echo "🚀 للتشغيل: python run_server.py"
echo "🌐 العنوان: http://localhost:5000"
echo "📞 الدعم: 771831482"
