# -*- coding: utf-8 -*-
"""
شاشة تسجيل مستخدم جديد - تصميم متكامل
"""
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from app.utils.arabic_support import ArabicSupport
from app.utils.api import API
from app.utils.validators import Validators

Builder.load_string('''
<RegisterScreen>:
    MDScreen:
        md_bg_color: app.theme_cls.primary_color if app.theme_cls.theme_style == "Dark" else [0.95, 0.95, 0.95, 1]
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(15)
            spacing: dp(10)
            
            # زر العودة
            MDBoxLayout:
                orientation: 'horizontal'
                adaptive_height: True
                padding: [0, dp(10), 0, dp(10)]
                
                MDFlatButton:
                    text: "← العودة"
                    font_name: 'DroidArabic'
                    theme_text_color: "Primary"
                    on_press: root.go_to_login()
                    size_hint_x: None
                    width: dp(100)
                
                MDLabel:
                    text: ""
                    size_hint_x: 1
            
            ScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(15)
                    adaptive_height: True
                    size_hint_y: None
                    height: self.minimum_height
                    
                    # العنوان
                    MDLabel:
                        text: "إنشاء حساب جديد"
                        font_style: 'H4'
                        theme_text_color: 'Primary'
                        halign: 'center'
                        font_name: 'DroidArabic'
                        bold: True
                        size_hint_y: None
                        height: dp(50)
                    
                    # معلومات الحساب
                    MDLabel:
                        text: "معلومات الحساب"
                        font_style: 'Subtitle1'
                        theme_text_color: 'Secondary'
                        halign: 'right'
                        font_name: 'DroidArabic'
                        bold: True
                        size_hint_y: None
                        height: dp(40)
                    
                    # الاسم الكامل
                    MDTextField:
                        id: full_name
                        hint_text: "الاسم الكامل *"
                        mode: "rectangle"
                        size_hint_x: 0.9
                        pos_hint: {'center_x': 0.5}
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                    
                    # البريد الإلكتروني
                    MDTextField:
                        id: email
                        hint_text: "البريد الإلكتروني *"
                        mode: "rectangle"
                        size_hint_x: 0.9
                        pos_hint: {'center_x': 0.5}
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                    
                    # رقم الهاتف
                    MDTextField:
                        id: phone
                        hint_text: "رقم الهاتف *"
                        mode: "rectangle"
                        size_hint_x: 0.9
                        pos_hint: {'center_x': 0.5}
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                        input_type: 'number'
                    
                    # معلومات المستخدم
                    MDLabel:
                        text: "معلومات المستخدم"
                        font_style: 'Subtitle1'
                        theme_text_color: 'Secondary'
                        halign: 'right'
                        font_name: 'DroidArabic'
                        bold: True
                        size_hint_y: None
                        height: dp(40)
                    
                    # اسم المستخدم
                    MDTextField:
                        id: username
                        hint_text: "اسم المستخدم *"
                        mode: "rectangle"
                        size_hint_x: 0.9
                        pos_hint: {'center_x': 0.5}
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                    
                    # كلمة المرور
                    MDTextField:
                        id: password
                        hint_text: "كلمة المرور *"
                        mode: "rectangle"
                        size_hint_x: 0.9
                        pos_hint: {'center_x': 0.5}
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                        password: True
                    
                    # تأكيد كلمة المرور
                    MDTextField:
                        id: confirm_password
                        hint_text: "تأكيد كلمة المرور *"
                        mode: "rectangle"
                        size_hint_x: 0.9
                        pos_hint: {'center_x': 0.5}
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                        password: True
                    
                    # نوع المستخدم
                    MDLabel:
                        text: "نوع المستخدم *"
                        font_style: 'Body1'
                        halign: 'right'
                        font_name: 'DroidArabic'
                        size_hint_x: 0.9
                        pos_hint: {'center_x': 0.5}
                        size_hint_y: None
                        height: dp(40)
                    
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: 0.9
                        size_hint_y: None
                        height: dp(50)
                        pos_hint: {'center_x': 0.5}
                        spacing: dp(10)
                        
                        MDTextField:
                            id: user_type
                            hint_text: "اختر نوع المستخدم"
                            mode: "rectangle"
                            size_hint_x: 0.8
                            font_name: 'DroidArabic'
                            text_direction: 'rtl'
                            readonly: True
                        
                        MDRaisedButton:
                            text: "اختر"
                            size_hint_x: 0.2
                            font_name: 'DroidArabic'
                            on_press: root.show_user_type_menu()
                    
                    # معلومات إضافية حسب نوع المستخدم
                    MDBoxLayout:
                        id: additional_fields
                        orientation: 'vertical'
                        size_hint_x: 0.9
                        pos_hint: {'center_x': 0.5}
                        spacing: dp(10)
                        adaptive_height: True
                        size_hint_y: None
                        height: self.minimum_height
                    
                    # شروط الخدمة
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: 0.9
                        size_hint_y: None
                        height: dp(50)
                        pos_hint: {'center_x': 0.5}
                        spacing: dp(10)
                        
                        MDCheckbox:
                            id: terms_check
                            size_hint: None, None
                            size: dp(40), dp(40)
                            active: False
                        
                        MDLabel:
                            text: "أوافق على شروط الخدمة وسياسة الخصوصية"
                            font_style: 'Body2'
                            halign: 'right'
                            font_name: 'DroidArabic'
                            theme_text_color: 'Secondary'
                            size_hint_x: 1
                    
                    # زر التسجيل
                    MDRaisedButton:
                        text: "إنشاء الحساب"
                        size_hint_x: 0.9
                        pos_hint: {'center_x': 0.5}
                        font_name: 'DroidArabic'
                        font_size: '18sp'
                        md_bg_color: app.theme_cls.primary_color
                        on_press: root.register()
                        height: dp(50)
                    
                    # مسافة
                    MDLabel:
                        text: ""
                        size_hint_y: None
                        height: dp(30)
''')

class RegisterScreen(Screen):
    """شاشة تسجيل مستخدم جديد"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = API()
        self.validators = Validators()
        self.user_type_menu = None
        self.dialog = None
        Clock.schedule_once(self.setup_ui)
    
    def setup_ui(self, dt):
        """إعداد واجهة المستخدم"""
        pass
    
    def show_user_type_menu(self):
        """عرض قائمة أنواع المستخدمين"""
        user_types = [
            {
                "text": "مشتري",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="مشتري": self.set_user_type(x),
            },
            {
                "text": "بائع",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="بائع": self.set_user_type(x),
            },
            {
                "text": "مندوب توصيل",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="مندوب توصيل": self.set_user_type(x),
            },
            {
                "text": "مغسلة قات",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="مغسلة قات": self.set_user_type(x),
            },
        ]
        
        self.user_type_menu = MDDropdownMenu(
            caller=self.ids.user_type,
            items=user_types,
            width_mult=4,
            max_height=dp(200),
        )
        self.user_type_menu.open()
    
    def set_user_type(self, user_type):
        """تعيين نوع المستخدم"""
        self.ids.user_type.text = user_type
        if self.user_type_menu:
            self.user_type_menu.dismiss()
        
        # إظهار الحقول الإضافية حسب نوع المستخدم
        self.show_additional_fields(user_type)
    
    def show_additional_fields(self, user_type):
        """إظهار الحقول الإضافية حسب نوع المستخدم"""
        additional_fields = self.ids.additional_fields
        additional_fields.clear_widgets()
        
        if user_type == "بائع":
            # اسم المتجر للمتجر
            store_field = MDTextField(
                hint_text="اسم المتجر",
                mode="rectangle",
                font_name='DroidArabic',
                text_direction='rtl',
                id="store_name"
            )
            additional_fields.add_widget(store_field)
            
            # عنوان المتجر
            address_field = MDTextField(
                hint_text="عنوان المتجر",
                mode="rectangle",
                font_name='DroidArabic',
                text_direction='rtl',
                id="store_address"
            )
            additional_fields.add_widget(address_field)
        
        elif user_type == "مندوب توصيل":
            # نوع المركبة
            vehicle_field = MDTextField(
                hint_text="نوع المركبة",
                mode="rectangle",
                font_name='DroidArabic',
                text_direction='rtl',
                id="vehicle_type"
            )
            additional_fields.add_widget(vehicle_field)
            
            # رقم المركبة
            plate_field = MDTextField(
                hint_text="رقم المركبة",
                mode="rectangle",
                font_name='DroidArabic',
                text_direction='rtl',
                id="vehicle_plate"
            )
            additional_fields.add_widget(plate_field)
        
        elif user_type == "مغسلة قات":
            # اسم المغسلة
            washer_field = MDTextField(
                hint_text="اسم المغسلة",
                mode="rectangle",
                font_name='DroidArabic',
                text_direction='rtl',
                id="washer_name"
            )
            additional_fields.add_widget(washer_field)
            
            # موقع المغسلة
            location_field = MDTextField(
                hint_text="موقع المغسلة",
                mode="rectangle",
                font_name='DroidArabic',
                text_direction='rtl',
                id="washer_location"
            )
            additional_fields.add_widget(location_field)
    
    def validate_form(self):
        """التحقق من صحة البيانات"""
        fields = {
            'full_name': self.ids.full_name,
            'email': self.ids.email,
            'phone': self.ids.phone,
            'username': self.ids.username,
            'password': self.ids.password,
            'confirm_password': self.ids.confirm_password,
            'user_type': self.ids.user_type
        }
        
        # التحقق من إدخال جميع الحقول المطلوبة
        for field_name, field in fields.items():
            if not field.text.strip():
                field.error = True
                field.helper_text = "هذا الحقل مطلوب"
                return False
            else:
                field.error = False
                field.helper_text = ""
        
        # التحقق من صحة البريد الإلكتروني
        if not self.validators.is_valid_email(self.ids.email.text):
            self.ids.email.error = True
            self.ids.email.helper_text = "بريد إلكتروني غير صالح"
            return False
        
        # التحقق من صحة رقم الهاتف
        if not self.validators.is_valid_phone(self.ids.phone.text):
            self.ids.phone.error = True
            self.ids.phone.helper_text = "رقم هاتف غير صالح"
            return False
        
        # التحقق من تطابق كلمات المرور
        if self.ids.password.text != self.ids.confirm_password.text:
            self.ids.password.error = True
            self.ids.confirm_password.error = True
            self.ids.password.helper_text = "كلمات المرور غير متطابقة"
            self.ids.confirm_password.helper_text = "كلمات المرور غير متطابقة"
            return False
        
        # التحقق من قوة كلمة المرور
        if not self.validators.is_strong_password(self.ids.password.text):
            self.ids.password.error = True
            self.ids.password.helper_text = "كلمة المرور ضعيفة (8 أحرف على الأقل)"
            return False
        
        # التحقق من قبول الشروط
        if not self.ids.terms_check.active:
            self.show_error("يجب الموافقة على شروط الخدمة")
            return False
        
        return True
    
    def register(self):
        """تسجيل مستخدم جديد"""
        if not self.validate_form():
            return
        
        # جمع بيانات المستخدم
        user_data = {
            'full_name': self.ids.full_name.text.strip(),
            'email': self.ids.email.text.strip(),
            'phone': self.ids.phone.text.strip(),
            'username': self.ids.username.text.strip(),
            'password': self.ids.password.text,
            'role': self.map_user_type(self.ids.user_type.text)
        }
        
        # إضافة البيانات الإضافية حسب نوع المستخدم
        if self.ids.user_type.text == "بائع":
            user_data['store_name'] = self.get_additional_field('store_name', '')
            user_data['store_address'] = self.get_additional_field('store_address', '')
        
        elif self.ids.user_type.text == "مندوب توصيل":
            user_data['vehicle_type'] = self.get_additional_field('vehicle_type', '')
            user_data['vehicle_plate'] = self.get_additional_field('vehicle_plate', '')
        
        elif self.ids.user_type.text == "مغسلة قات":
            user_data['washer_name'] = self.get_additional_field('washer_name', '')
            user_data['washer_location'] = self.get_additional_field('washer_location', '')
        
        # إظهار تحميل
        self.show_loading()
        
        # إرسال طلب التسجيل
        def on_success(response):
            self.hide_loading()
            if response.get('success'):
                # حفظ بيانات المستخدم
                app = self.manager.app
                app.user_data = response.get('user', {})
                app.user_token = response.get('token')
                
                # تحميل الإشعارات
                Clock.schedule_once(lambda dt: app.load_notifications())
                
                # الانتقال للشاشة المناسبة
                role = app.user_data.get('role', 'buyer')
                if role == 'admin':
                    self.manager.current = 'admin_dashboard'
                elif role == 'seller':
                    self.manager.current = 'seller_dashboard'
                elif role == 'driver':
                    self.manager.current = 'driver_dashboard'
                elif role == 'washer':
                    self.manager.current = 'home'
                else:
                    self.manager.current = 'home'
                
                self.show_success("تم إنشاء الحساب بنجاح!")
            else:
                self.show_error(response.get('message', 'فشل إنشاء الحساب'))
        
        def on_error(error):
            self.hide_loading()
            self.show_error("خطأ في الاتصال بالسيرفر")
        
        self.api.register(user_data, on_success, on_error)
    
    def get_additional_field(self, field_id, default):
        """الحصول على قيمة حقل إضافي"""
        additional_fields = self.ids.additional_fields
        for child in additional_fields.children:
            if hasattr(child, 'id') and child.id == field_id:
                return child.text.strip()
        return default
    
    def map_user_type(self, arabic_type):
        """تحويل نوع المستخدم العربي إلى إنجليزي"""
        mapping = {
            'مشتري': 'buyer',
            'بائع': 'seller',
            'مندوب توصيل': 'driver',
            'مغسلة قات': 'washer'
        }
        return mapping.get(arabic_type, 'buyer')
    
    def go_to_login(self):
        """الذهاب لشاشة تسجيل الدخول"""
        self.manager.current = 'login'
    
    def show_loading(self):
        """إظهار نافذة التحميل"""
        if not hasattr(self, 'loading_dialog'):
            self.loading_dialog = MDDialog(
                title="جاري إنشاء الحساب...",
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
