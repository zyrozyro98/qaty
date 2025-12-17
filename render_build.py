#!/usr/bin/env python3
"""
سكريبت البناء لـ Render.com
"""
import os
import sys
import subprocess
from pathlib import Path

print("🚀 بدء بناء تطبيق قات على Render...")

# إنشاء الهيكل الأساسي للمجلدات
folders = [
    'logs',
    'uploads',
    'static',
    'templates'
]

for folder in folders:
    Path(folder).mkdir(exist_ok=True)
    print(f"✅ تم إنشاء مجلد: {folder}")

# تحديث المسارات
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# التحقق من متغيرات البيئة
required_env_vars = ['SECRET_KEY', 'API_KEY', 'DATABASE_URL']
missing_vars = []

for var in required_env_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"⚠️  متغيرات البيئة المفقودة: {missing_vars}")
else:
    print("✅ جميع متغيرات البيئة موجودة")

print("✅ اكتمل البناء بنجاح!")
