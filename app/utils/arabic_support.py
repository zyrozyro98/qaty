# -*- coding: utf-8 -*-
"""
دعم كامل للغة العربية في Kivy
حل مشاكل النصوص المعكوسة والرموز الغير مفهومة
"""
import os
from kivy.core.text import LabelBase
from kivy.config import Config

class ArabicSupport:
    """فئة دعم اللغة العربية"""
    
    @staticmethod
    def setup_arabic_support():
        """إعداد دعم اللغة العربية"""
        # تعيين اتجاه النص من اليمين لليسار
        Config.set('kivy', 'text_direction', 'rtl')
        
        # تسجيل الخطوط العربية
        fonts_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts')
        
        # التحقق من وجود الخطوط
        required_fonts = [
            'DroidKufi-Regular.ttf',
            'DroidKufi-Bold.ttf',
            'NotoSansArabic-Regular.ttf'
        ]
        
        for font in required_fonts:
            font_path = os.path.join(fonts_dir, font)
            if os.path.exists(font_path):
                try:
                    if 'Regular' in font:
                        LabelBase.register(name='DroidArabic',
                                         fn_regular=font_path)
                    elif 'Bold' in font:
                        LabelBase.register(name='DroidArabic-Bold',
                                         fn_regular=font_path)
                except:
                    pass
        
        # إعدادات إضافية للنصوص العربية
        Config.set('kivy', 'default_font', ['DroidArabic', 'assets/fonts/DroidKufi-Regular.ttf'])
    
    @staticmethod
    def arabic_text(text):
        """معالجة النص العربي لضمان ظهوره بشكل صحيح"""
        if not text:
            return text
        
        # إصلاح مشاكل النصوص العربية
        text = text.strip()
        
        # قائمة بالكلمات التي تحتاج لمعالجة خاصة
        arabic_fixes = {
            'ه': 'ه',  # إصلاح الهاء
            'ي': 'ي',  # إصلاح الياء
            'ك': 'ك',  # إصلاح الكاف
            'ة': 'ة',  # إصلاح التاء المربوطة
        }
        
        # تطبيق الإصلاحات
        for wrong, correct in arabic_fixes.items():
            text = text.replace(wrong, correct)
        
        return text
    
    @staticmethod
    def is_arabic(text):
        """فحص إذا كان النص عربي"""
        try:
            arabic_chars = set('ابپتثجچحخدذرزژسشصضطظعغفقكکگلمنوهیئؤإأآةى')
            return any(char in arabic_chars for char in text)
        except:
            return False
