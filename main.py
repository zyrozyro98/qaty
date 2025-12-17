# -*- coding: utf-8 -*-
"""
تطبيق قات - تطبيق كامل لبيع وتوصيل القات
الإصدار: 1.0.0
Python 3.13
"""
import sys
import os
from pathlib import Path

# إضافة المسار الحالي لـ Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """الدالة الرئيسية للتطبيق"""
    try:
        from app.main_app import QatApp
        app = QatApp()
        app.run()
    except Exception as e:
        print(f"خطأ في تشغيل التطبيق: {e}")
        import traceback
        traceback.print_exc()
        input("اضغط Enter للخروج...")

if __name__ == '__main__':
    main()