# -*- coding: utf-8 -*-
"""
مكون نص عربي مخصص يحل مشاكل الإدخال والظهور
"""
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.window import Window
from kivy.clock import Clock

class ArabicTextInput(TextInput):
    """مكون إدخال نص عربي"""
    
    arabic_hint = StringProperty('')
    is_password = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.padding = [10, 10]
        self.halign = 'right'
        self.font_name = 'DroidArabic'
        self.font_size = '16sp'
        
        # إعداد خاص للغة العربية
        self.bind(text=self.on_text_change)
        
        # إصلاح مشكلة الاتجاه
        self.text_direction = 'rtl'
    
    def on_text_change(self, instance, value):
        """معالجة تغيير النص"""
        if value:
            # إصلاح النص العربي
            from ..utils.arabic_support import ArabicSupport
            self.text = ArabicSupport.arabic_text(value)
    
    def on_focus(self, instance, value):
        """معالجة التركيز"""
        super().on_focus(instance, value)
        if value:
            # عند التركيز، تأكد من اتجاه النص
            Clock.schedule_once(lambda dt: self._fix_cursor_position())
    
    def _fix_cursor_position(self):
        """إصلاح موضع المؤشر للنصوص العربية"""
        if self.text:
            self.cursor = (len(self.text), 0)
    
    def insert_text(self, substring, from_undo=False):
        """إدخال نص مع معالجة خاصة للعربية"""
        if substring:
            # معالجة النص المدخل
            from ..utils.arabic_support import ArabicSupport
            substring = ArabicSupport.arabic_text(substring)
        
        return super().insert_text(substring, from_undo)
