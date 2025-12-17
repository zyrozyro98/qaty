# -*- coding: utf-8 -*-
"""
شاشة تسجيل مستخدم جديد - تصميم متكامل مع دعم عربي
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
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.scrollview import MDScrollView

from app.utils.arabic_support import ArabicSupport
from app.utils.api import API

Builder.load_string('''
<RegisterScreen>:
    MDScreen:
        md_bg_color: app.theme_cls.primary_color if app.theme_cls.theme_style == "Dark" else [0.95, 0.95, 0.95, 1]
        
        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(15)
                size_hint_y: None
                height: self.minimum_height
                adaptive_height: True
                
                # العودة لتسجيل الدخول
                MDBoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(40)
                    padding: [0, 0, dp(10), 0]
                    
                    MDFlatButton:
                        text: "← العودة"
                        font_name: 'DroidArabic'
                        theme_text_color: "Primary"
                        on_press: root.go_to_login()
                        size_hint_x: None
                        width: dp(80)
                
                # عنوان الشاشة
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(5)
                    size_hint_y: None
                    height: dp(100)
                    adaptive_height: True
                    padding: [dp(20), 0]
                    
                    MDLabel:
                        text: "🌿"
                        font_size: '40sp'
                        halign: 'center'
                        size_hint_y: None
                        height: dp(50)
                    
                    MDLabel:
                        text: "إنشاء حساب جديد"
                        font_style: 'H4'
                        theme_text_color: 'Primary'
                        halign: 'center'
                        font_name: 'DroidArabic'
                        bold: True
                        size_hint_y: None
                        height: dp(50)
                
                # نموذج التسجيل
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(15)
                    size_hint_y: None
                    height: self.minimum_height
                    adaptive_height: True
                    
                    # الاسم الكامل
                    MDTextField:
                        id: full_name_input
                        hint_text: "الاسم الكامل"
                        icon_left: "account"
                        mode: "rectangle"
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                    
                    # البريد الإلكتروني
                    MDTextField:
                        id: email_input
                        hint_text: "البريد الإلكتروني"
                        icon_left: "email"
                        mode: "rectangle"
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                    
                    # رقم الهاتف
                    MDTextField:
                        id: phone_input
                        hint_text: "رقم الهاتف"
                        icon_left: "phone"
                        mode: "rectangle"
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                    
                    # اسم المستخدم
                    MDTextField:
                        id: username_input
                        hint_text: "اسم المستخدم"
                        icon_left: "account-circle"
                        mode: "rectangle"
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                    
                    # كلمة المرور
                    MDTextField:
                        id: password_input
                        hint_text: "كلمة المرور"
                        icon_left: "key"
                        mode: "rectangle"
                        password: True
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                    
                    # تأكيد كلمة المرور
                    MDTextField:
                        id: confirm_password_input
                        hint_text: "تأكيد كلمة المرور"
                        icon_left: "key-change"
                        mode: "rectangle"
                        password: True
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        helper_text_mode: "on_error"
                    
                    # نوع المستخدم
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(60)
                        
                        MDLabel:
                            text: "نوع المستخدم:"
                            font_name: 'DroidArabic'
                            size_hint_x: 0.4
                            height: dp(50)
                            valign: 'center'
                        
                        MDTextField:
                            id: user_type_input
                            hint_text: "اختر نوع المستخدم"
                            mode: "rectangle"
                            readonly: True
                            font_name: 'DroidArabic'
                            on_focus: if self.focus: root.show_user_type_dialog()
                    
                    # حقول إضافية حسب نوع المستخدم
                    MDTextField:
                        id: store_name_input
                        hint_text: "اسم المتجر (للبائعين)"
                        icon_left: "store"
                        mode: "rectangle"
                        font_name: 'DroidArabic'
                        opacity: 0
                        height: 0
                        size_hint_y: None
                    
                    MDTextField:
                        id: vehicle_type_input
                        hint_text: "نوع المركبة (لمندوبي التوصيل)"
                        icon_left: "car"
                        mode: "rectangle"
                        font_name: 'DroidArabic'
                        opacity: 0
                        height: 0
                        size_hint_y: None
                    
                    # اتفاقية الشروط
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(50)
                        
                        MDCheckbox:
                            id: terms_checkbox
                            size_hint: None, None
                            size: dp(40), dp(40)
                        
                        MDLabel:
                            text: "أوافق على شروط الاستخدام وسياسة الخصوصية"
                            font_name: 'DroidArabic'
                            font_size: '14sp'
                            theme_text_color: "Secondary"
                            size_hint_x: 1
                            on_ref_press: root.show_terms_dialog
                    
                    # زر إنشاء الحساب
                    MDRaisedButton:
                        id: register_button
                        text: "إنشاء الحساب"
                        size_hint_x: 0.9
                        pos_hint: {'center_x': 0.5}
                        font_name: 'DroidArabic'
                        font_size: '18sp'
                        md_bg_color: app.theme_cls.primary_color
                        on_press: root.register()
                        height: dp(50)
                        disabled: True
''')

class RegisterScreen(Screen):
    """شاشة تسجيل مستخدم جديد"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = API()
        self.dialog = None
        self.user_type_dialog = None
        self.terms_dialog = None
        Clock.schedule_once(self.setup_ui)
    
    def setup_ui(self, dt):
        """إعداد واجهة المستخدم"""
        # ربط حدث تغيير النص للتحقق من الحقول
        fields = ['full_name_input', 'email_input', 'phone_input', 
                 'username_input', 'password_input', 'confirm_password_input']
        
        for field_id in fields:
            field = self.ids[field_id]
            field.bind(text=self.validate_form)
        
        # ربط حدث تغيير حالة الشروط
        self.ids.terms_checkbox.bind(active=self.validate_form)
    
    def validate_form(self, *args):
        """التحقق من صحة النموذج"""
        # التحقق من جميع الحقول المطلوبة
        required_fields = [
            ('full_name_input', 'الاسم الكامل'),
            ('email_input', 'البريد الإلكتروني'),
            ('phone_input', 'رقم الهاتف'),
            ('username_input', 'اسم المستخدم'),
            ('password_input', 'كلمة المرور'),
            ('confirm_password_input', 'تأكيد كلمة المرور')
        ]
        
        all_valid = True
        error_messages = []
        
        for field_id, field_name in required_fields:
            field = self.ids[field_id]
            if not field.text.strip():
                all_valid = False
                field.error = True
                field.helper_text = f"{field_name} مطلوب"
            else:
                field.error = False
                field.helper_text = ""
                
                # تحقق خاص لكل حقل
                if field_id == 'email_input' and '@' not in field.text:
                    all_valid = False
                    field.error = True
                    field.helper_text = "البريد الإلكتروني غير صحيح"
                
                elif field_id == 'phone_input' and not field.text.strip().isdigit():
                    all_valid = False
                    field.error = True
                    field.helper_text = "رقم الهاتف يجب أن يكون أرقام فقط"
                
                elif field_id == 'confirm_password_input':
                    password = self.ids.password_input.text
                    confirm = field.text
                    if password != confirm:
                        all_valid = False
                        field.error = True
                        field.helper_text = "كلمات المرور غير متطابقة"
                        self.ids.password_input.error = True
                        self.ids.password_input.helper_text = "كلمات المرور غير متطابقة"
        
        # التحقق من نوع المستخدم
        user_type = self.ids.user_type_input.text
        if not user_type or user_type == "اختر نوع المستخدم":
            all_valid = False
        
        # التحقق من الشروط
        if not self.ids.terms_checkbox.active:
            all_valid = False
        
        # تفعيل/تعطيل زر التسجيل
        self.ids.register_button.disabled = not all_valid
        
        return all_valid
    
    def show_user_type_dialog(self):
        """عرض نافذة اختيار نوع المستخدم"""
        user_types = [
            ("مشتري", "account", "لشراء المنتجات"),
            ("بائع", "store", "لعرض وبيع المنتجات"),
            ("مندوب توصيل", "truck-delivery", "لتوصيل الطلبات"),
            ("مشغل مغسلة", "water", "لغسل القات")
        ]
        
        dialog_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(350)
        )
        
        for type_name, icon, description in user_types:
            item_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(70)
            )
            
            item_layout.add_widget(MDIcon(icon=icon, size_hint_x=None, width=dp(40)))
            
            text_layout = MDBoxLayout(
                orientation='vertical',
                spacing=dp(2)
            )
            text_layout.add_widget(MDLabel(
                text=type_name,
                font_name='DroidArabic',
                bold=True
            ))
            text_layout.add_widget(MDLabel(
                text=description,
                font_name='DroidArabic',
                font_size='12sp',
                theme_text_color='Secondary'
            ))
            
            item_layout.add_widget(text_layout)
            item_layout.add_widget(MDBoxLayout())  # spacer
            
            # جعل العنصر قابلاً للنقر
            item_layout.bind(on_touch_down=lambda x, y, t=type_name: self.select_user_type(t, y))
            dialog_content.add_widget(item_layout)
        
        self.user_type_dialog = MDDialog(
            title="اختر نوع المستخدم",
            type="custom",
            content_cls=dialog_content,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    font_name='DroidArabic',
                    on_press=lambda x: self.user_type_dialog.dismiss()
                )
            ]
        )
        self.user_type_dialog.open()
    
    def select_user_type(self, user_type, touch):
        """اختيار نوع المستخدم"""
        if touch.is_double_tap or touch.is_mouse_scrolling:
            return False
        
        self.ids.user_type_input.text = user_type
        
        # إظهار/إخفاء الحقول الإضافية
        if user_type == 'بائع':
            self.ids.store_name_input.opacity = 1
            self.ids.store_name_input.height = dp(50)
            self.ids.vehicle_type_input.opacity = 0
            self.ids.vehicle_type_input.height = 0
        elif user_type == 'مندوب توصيل':
            self.ids.store_name_input.opacity = 0
            self.ids.store_name_input.height = 0
            self.ids.vehicle_type_input.opacity = 1
            self.ids.vehicle_type_input.height = dp(50)
        else:
            self.ids.store_name_input.opacity = 0
            self.ids.store_name_input.height = 0
            self.ids.vehicle_type_input.opacity = 0
            self.ids.vehicle_type_input.height = 0
        
        if self.user_type_dialog:
            self.user_type_dialog.dismiss()
        
        self.validate_form()
        return True
    
    def show_terms_dialog(self, *args):
        """عرض شروط الاستخدام"""
        terms_text = """
        شروط استخدام تطبيق قات:
        
        1. الالتزام بالقوانين المحلية والدولية.
        2. عدم استخدام التطبيق لأغراض غير قانونية.
        3. الحفاظ على خصوصية البيانات.
        4. المسؤولية الكاملة عن المعاملات المالية.
        5. يحق للإدارة تعليق الحساب في حالة المخالفة.
        
        سياسة الخصوصية:
        1. نحن نحافظ على خصوصية بياناتك.
        2. لا نشارك بياناتك مع طرف ثالث دون موافقتك.
        3. نستخدم البيانات فقط لتحسين الخدمة.
        4. يمكنك طلب حذف بياناتك في أي وقت.
        
        للمزيد من المعلومات:
        support@qat-app.com
        """
        
        self.terms_dialog = MDDialog(
            title="شروط الاستخدام وسياسة الخصوصية",
            text=ArabicSupport.arabic_text(terms_text),
            buttons=[
                MDFlatButton(
                    text="موافق",
                    font_name='DroidArabic',
                    on_press=lambda x: self.terms_dialog.dismiss()
                )
            ]
        )
        self.terms_dialog.open()
    
    def register(self):
        """تسجيل مستخدم جديد"""
        if not self.validate_form():
            self.show_error("يرجى تعبئة جميع الحقول المطلوبة بشكل صحيح")
            return
        
        # جمع بيانات المستخدم
        user_data = {
            'full_name': self.ids.full_name_input.text.strip(),
            'email': self.ids.email_input.text.strip(),
            'phone': self.ids.phone_input.text.strip(),
            'username': self.ids.username_input.text.strip(),
            'password': self.ids.password_input.text,
            'role': self.map_user_type(self.ids.user_type_input.text),
            'store_name': self.ids.store_name_input.text.strip() if self.ids.user_type_input.text == 'بائع' else '',
            'vehicle_type': self.ids.vehicle_type_input.text.strip() if self.ids.user_type_input.text == 'مندوب توصيل' else ''
        }
        
        # إظهار تحميل
        self.show_loading("جاري إنشاء الحساب...")
        
        # إرسال طلب التسجيل
        def on_register_success(response):
            self.hide_loading()
            
            if response.get('success'):
                # حفظ بيانات المستخدم
                app = self.manager.app
                app.user_data = response.get('user', {})
                app.user_token = response.get('token', '')
                
                # تنظيف الحقول
                self.clear_fields()
                
                # الانتقال للشاشة المناسبة
                role = response.get('user', {}).get('role', 'buyer')
                if role == 'admin':
                    self.manager.current = 'admin_dashboard'
                elif role == 'seller':
                    self.manager.current = 'seller_dashboard'
                else:
                    self.manager.current = 'home'
                
                self.show_success("تم إنشاء الحساب بنجاح!")
            else:
                self.show_error(response.get('message', 'فشل إنشاء الحساب'))
        
        def on_register_error(error):
            self.hide_loading()
            self.show_error("خطأ في الاتصال بالسيرفر")
        
        # استخدام API
        self.api.register(user_data, on_register_success, on_register_error)
    
    def map_user_type(self, arabic_type):
        """تحويل نوع المستخدم من عربي لإنجليزي"""
        mapping = {
            'مشتري': 'buyer',
            'بائع': 'seller',
            'مندوب توصيل': 'driver',
            'مشغل مغسلة': 'washer'
        }
        return mapping.get(arabic_type, 'buyer')
    
    def clear_fields(self):
        """مسح جميع الحقول"""
        fields = ['full_name_input', 'email_input', 'phone_input',
                 'username_input', 'password_input', 'confirm_password_input',
                 'user_type_input', 'store_name_input', 'vehicle_type_input']
        
        for field_id in fields:
            field = self.ids[field_id]
            field.text = ""
            field.error = False
            field.helper_text = ""
        
        self.ids.terms_checkbox.active = False
        self.ids.store_name_input.opacity = 0
        self.ids.store_name_input.height = 0
        self.ids.vehicle_type_input.opacity = 0
        self.ids.vehicle_type_input.height = 0
    
    def go_to_login(self):
        """الذهاب لشاشة تسجيل الدخول"""
        self.clear_fields()
        self.manager.current = 'login'
    
    def show_loading(self, message="جاري التحميل..."):
        """إظهار نافذة التحميل"""
        self.loading_dialog = MDDialog(
            title=message,
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=dp(20),
                size_hint_y=None,
                height=dp(100)
            ),
            auto_dismiss=False
        )
        
        # إضافة spinner
        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={'center_x': 0.5}
        )
        self.loading_dialog.content_cls.add_widget(spinner)
        
        self.loading_dialog.open()
    
    def hide_loading(self):
        """إخفاء نافذة التحميل"""
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.dismiss()
    
    def show_error(self, message):
        """إظهار رسالة خطأ"""
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
        """إظهار رسالة نجاح"""
        self.dialog = MDDialog(
            title="تم بنجاح",
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
