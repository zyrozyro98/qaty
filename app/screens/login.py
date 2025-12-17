# -*- coding: utf-8 -*-
"""
شاشة تسجيل الدخول - تصميم متكامل مع دعم عربي كامل
"""
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from app.utils.arabic_support import ArabicSupport
from app.utils.api import API

Builder.load_string('''
<LoginScreen>:
    MDScreen:
        md_bg_color: app.theme_cls.primary_color if app.theme_cls.theme_style == "Dark" else [0.95, 0.95, 0.95, 1]
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(20)
            adaptive_height: True
            size_hint_y: None
            height: self.minimum_height
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(20)
                size_hint_y: None
                height: self.minimum_height
                adaptive_height: True
                
                # شعار التطبيق
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(10)
                    size_hint_y: None
                    height: self.minimum_height
                    adaptive_height: True
                    padding: dp(10)
                    
                    MDLabel:
                        text: "🌿"
                        font_size: '50sp'
                        halign: 'center'
                        size_hint_y: None
                        height: dp(60)
                    
                    MDLabel:
                        text: "تطبيق قات"
                        font_style: 'H4'
                        theme_text_color: 'Primary'
                        halign: 'center'
                        font_name: 'DroidArabic'
                        bold: True
                        size_hint_y: None
                        height: dp(50)
                    
                    MDLabel:
                        text: "منصة بيع وتوصيل القات"
                        font_style: 'Subtitle1'
                        theme_text_color: 'Secondary'
                        halign: 'center'
                        font_name: 'DroidArabic'
                        size_hint_y: None
                        height: dp(40)
                
                # حقل اسم المستخدم
                MDTextField:
                    id: username_input
                    hint_text: "اسم المستخدم"
                    icon_left: "account"
                    mode: "rectangle"
                    size_hint_x: 0.9
                    pos_hint: {'center_x': 0.5}
                    font_name: 'DroidArabic'
                    text_direction: 'rtl'
                    helper_text_mode: "on_error"
                
                # حقل كلمة المرور
                MDTextField:
                    id: password_input
                    hint_text: "كلمة المرور"
                    icon_left: "key"
                    mode: "rectangle"
                    password: True
                    size_hint_x: 0.9
                    pos_hint: {'center_x': 0.5}
                    font_name: 'DroidArabic'
                    text_direction: 'rtl'
                    helper_text_mode: "on_error"
                
                # زر تسجيل الدخول
                MDRaisedButton:
                    text: "تسجيل الدخول"
                    size_hint_x: 0.9
                    pos_hint: {'center_x': 0.5}
                    font_name: 'DroidArabic'
                    font_size: '18sp'
                    md_bg_color: app.theme_cls.primary_color
                    on_press: root.login()
                    height: dp(50)
                
                # زر إنشاء حساب
                MDFlatButton:
                    text: "إنشاء حساب جديد"
                    size_hint_x: 0.9
                    pos_hint: {'center_x': 0.5}
                    font_name: 'DroidArabic'
                    theme_text_color: "Primary"
                    on_press: root.go_to_register()
                    height: dp(40)
                
                # نسيت كلمة المرور
                MDFlatButton:
                    text: "نسيت كلمة المرور؟"
                    size_hint_x: 0.9
                    pos_hint: {'center_x': 0.5}
                    font_name: 'DroidArabic'
                    theme_text_color: "Hint"
                    font_size: '14sp'
                    on_press: root.show_forgot_password()
                    height: dp(30)
            
            # نسخة التطبيق
            MDLabel:
                text: "الإصدار 1.0.0"
                font_style: 'Caption'
                theme_text_color: "Hint"
                halign: 'center'
                font_name: 'DroidArabic'
                size_hint_y: None
                height: dp(30)
''')

class LoginScreen(Screen):
    """شاشة تسجيل الدخول"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.api = API()
        Clock.schedule_once(self.setup_ui)
    
    def setup_ui(self, dt):
        """إعداد واجهة المستخدم"""
        pass
    
    def login(self):
        """تسجيل الدخول"""
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        
        # التحقق من الحقول
        if not username or not password:
            self.show_error("يرجى إدخال اسم المستخدم وكلمة المرور")
            return
        
        # إظهار تحميل
        self.show_loading()
        
        # محاولة تسجيل الدخول
        def on_login_success(response):
            self.hide_loading()
            if response.get('success'):
                # حفظ بيانات المستخدم
                user_data = response.get('user', {})
                app = self.manager.app
                app.user_data = user_data
                app.user_token = response.get('token')
                
                # تحميل الإشعارات
                Clock.schedule_once(lambda dt: app.load_notifications())
                
                # الانتقال للشاشة المناسبة حسب نوع المستخدم
                role = user_data.get('role', 'buyer')
                if role == 'admin':
                    self.manager.current = 'admin_dashboard'
                elif role == 'seller':
                    self.manager.current = 'seller_dashboard'
                elif role == 'driver':
                    self.manager.current = 'driver_dashboard'
                else:
                    self.manager.current = 'home'
                
                self.show_success("تم تسجيل الدخول بنجاح")
            else:
                self.show_error(response.get('message', 'فشل تسجيل الدخول'))
        
        def on_login_error(error):
            self.hide_loading()
            self.show_error("خطأ في الاتصال بالسيرفر")
        
        # استخدام API الحقيقي أو المحاكاة
        if self.api.is_online():
            self.api.login(username, password, on_login_success, on_login_error)
        else:
            # محاكاة تسجيل الدخول للاختبار
            Clock.schedule_once(lambda dt: self.mock_login(username, password), 1)
    
    def mock_login(self, username, password):
        """محاكاة تسجيل الدخول للاختبار"""
        # بيانات مستخدم وهمية للاختبار
        test_users = {
            'admin': {'id': 1, 'role': 'admin', 'name': 'المدير العام'},
            'seller': {'id': 2, 'role': 'seller', 'name': 'بائع تجريبي'},
            'buyer': {'id': 3, 'role': 'buyer', 'name': 'مشتري تجريبي'},
            'driver': {'id': 4, 'role': 'driver', 'name': 'مندوب توصيل'}
        }
        
        if username in test_users and password == '123456':
            user_data = test_users[username]
            user_data['username'] = username
            user_data['email'] = f'{username}@example.com'
            user_data['phone'] = '771234567'
            user_data['wallet_balance'] = 1000.0
            
            app = self.manager.app
            app.user_data = user_data
            app.user_token = 'mock-token-123'
            
            # الانتقال للشاشة المناسبة
            role = user_data.get('role')
            if role == 'admin':
                self.manager.current = 'admin_dashboard'
            elif role == 'seller':
                self.manager.current = 'seller_dashboard'
            elif role == 'driver':
                self.manager.current = 'driver_dashboard'
            else:
                self.manager.current = 'home'
            
            self.show_success(f"مرحباً {user_data['name']}")
        else:
            self.show_error("اسم المستخدم أو كلمة المرور غير صحيحة")
    
    def go_to_register(self):
        """الذهاب لشاشة التسجيل"""
        self.manager.current = 'register'
    
    def show_forgot_password(self):
        """عرض نافذة نسيت كلمة المرور"""
        dialog_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(150)
        )
        
        dialog_content.add_widget(MDLabel(
            text="أدخل بريدك الإلكتروني لإعادة تعيين كلمة المرور",
            font_name='DroidArabic',
            halign='center'
        ))
        
        email_input = MDTextField(
            hint_text="البريد الإلكتروني",
            mode="rectangle",
            font_name='DroidArabic'
        )
        dialog_content.add_widget(email_input)
        
        def reset_password(instance):
            email = email_input.text
            if email:
                self.show_success(f"تم إرسال رابط إعادة التعيين إلى {email}")
                self.dialog.dismiss()
            else:
                email_input.error = True
                email_input.helper_text = "يرجى إدخال البريد الإلكتروني"
        
        self.dialog = MDDialog(
            title="نسيت كلمة المرور",
            type="custom",
            content_cls=dialog_content,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    font_name='DroidArabic',
                    on_press=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="إرسال",
                    font_name='DroidArabic',
                    on_press=reset_password
                )
            ]
        )
        self.dialog.open()
    
    def show_loading(self):
        """إظهار نافذة التحميل"""
        if not hasattr(self, 'loading_dialog'):
            self.loading_dialog = MDDialog(
                title="جاري تسجيل الدخول...",
                type="alert",
                auto_dismiss=False
            )
        self.loading_dialog.open()
    
    def hide_loading(self):
        """إخفاء نافذة التحميل"""
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.dismiss()
    
    def show_error(self, message):
        """إظهار خطأ"""
        self.dialog = MDDialog(
            title="خطأ",
            text=ArabicSupport.arabic_text(message),
            buttons=[
                MDFlatButton(
                    text="حسناً",
                    font_name='DroidArabic',
                    on_press=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def show_success(self, message):
        """إظهار نجاح"""
        self.dialog = MDDialog(
            title="تم",
            text=ArabicSupport.arabic_text(message),
            buttons=[
                MDFlatButton(
                    text="حسناً",
                    font_name='DroidArabic',
                    on_press=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
