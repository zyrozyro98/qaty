# -*- coding: utf-8 -*-
"""
شاشة الرئيسية - تصميم متكامل مع دعم عربي
"""
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.metrics import dp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior

from app.utils.arabic_support import ArabicSupport

Builder.load_string('''
<HomeCard>:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(10)
    size_hint: None, None
    size: dp(160), dp(160)
    elevation: 2
    radius: dp(15)
    
    MDIconButton:
        icon: root.icon
        icon_size: dp(40)
        pos_hint: {'center_x': 0.5}
        theme_icon_color: "Custom"
        icon_color: root.icon_color
    
    MDLabel:
        text: root.title
        font_style: 'Subtitle1'
        theme_text_color: "Primary"
        halign: 'center'
        font_name: 'DroidArabic'
        bold: True
        size_hint_y: None
        height: dp(40)
    
    MDLabel:
        text: root.subtitle
        font_style: 'Caption'
        theme_text_color: "Secondary"
        halign: 'center'
        font_name: 'DroidArabic'
        size_hint_y: None
        height: dp(30)

<HomeScreen>:
    MDScreen:
        md_bg_color: [0.95, 0.95, 0.95, 1]
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            
            # شريط العنوان
            MDBoxLayout:
                orientation: 'horizontal'
                adaptive_height: True
                padding: dp(10)
                spacing: dp(10)
                
                MDIconButton:
                    icon: "menu"
                    on_release: app.nav_drawer.set_state("open")
                
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(2)
                    
                    MDLabel:
                        text: "مرحباً بك في تطبيق قات"
                        font_style: 'H6'
                        theme_text_color: "Primary"
                        font_name: 'DroidArabic'
                        bold: True
                        size_hint_y: None
                        height: dp(30)
                    
                    MDLabel:
                        id: welcome_label
                        text: ""
                        font_style: 'Body2'
                        theme_text_color: "Secondary"
                        font_name: 'DroidArabic'
                        size_hint_y: None
                        height: dp(25)
                
                MDIconButton:
                    icon: "bell"
                    badge_text: str(root.unread_notifications) if root.unread_notifications > 0 else ""
                    on_release: root.show_notifications()
            
            # الإعلانات
            MDCard:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(180)
                padding: dp(10)
                spacing: dp(10)
                elevation: 1
                radius: dp(10)
                md_bg_color: [0.2, 0.7, 0.3, 0.1]
                
                MDLabel:
                    text: "إعلانات مميزة"
                    font_style: 'Subtitle1'
                    theme_text_color: "Primary"
                    halign: 'center'
                    font_name: 'DroidArabic'
                    bold: True
                    size_hint_y: None
                    height: dp(30)
                
                MDScrollView:
                    MDGridLayout:
                        id: ads_container
                        cols: 3
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(100)
                        adaptive_height: True
            
            # الأقسام الرئيسية
            MDLabel:
                text: "خدماتنا"
                font_style: 'H6'
                theme_text_color: "Primary"
                halign: 'right'
                padding: [dp(20), dp(10), dp(20), 0]
                font_name: 'DroidArabic'
                bold: True
                size_hint_y: None
                height: dp(40)
            
            MDScrollView:
                MDGridLayout:
                    id: services_grid
                    cols: 3
                    spacing: dp(15)
                    padding: dp(20)
                    size_hint_y: None
                    height: self.minimum_height
                    adaptive_height: True
            
            # إحصائيات سريعة
            MDCard:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(120)
                padding: dp(15)
                spacing: dp(10)
                elevation: 1
                radius: dp(10)
                
                MDLabel:
                    text: "إحصائيات سريعة"
                    font_style: 'Subtitle1'
                    theme_text_color: "Primary"
                    halign: 'center'
                    font_name: 'DroidArabic'
                    bold: True
                    size_hint_y: None
                    height: dp(30)
                
                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(10)
                    
                    MDLabel:
                        id: products_count
                        text: "المنتجات: 0"
                        font_style: 'Body2'
                        theme_text_color: "Secondary"
                        halign: 'center'
                        font_name: 'DroidArabic'
                        size_hint_x: 0.33
                    
                    MDLabel:
                        id: orders_count
                        text: "الطلبات: 0"
                        font_style: 'Body2'
                        theme_text_color: "Secondary"
                        halign: 'center'
                        font_name: 'DroidArabic'
                        size_hint_x: 0.33
                    
                    MDLabel:
                        id: balance_label
                        text: "الرصيد: 0 ريال"
                        font_style: 'Body2'
                        theme_text_color: "Secondary"
                        halign: 'center'
                        font_name: 'DroidArabic'
                        size_hint_x: 0.33
''')

class HomeCard(MDCard, RoundedRectangularElevationBehavior):
    """بطاقة الشاشة الرئيسية"""
    title = StringProperty('')
    subtitle = StringProperty('')
    icon = StringProperty('')
    icon_color = ListProperty([0.2, 0.7, 0.3, 1])

class HomeScreen(Screen):
    """شاشة الرئيسية"""
    
    unread_notifications = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.setup_home)
    
    def on_enter(self):
        """عند دخول الشاشة"""
        self.update_welcome_message()
        self.load_ads()
        self.load_services()
        self.update_stats()
    
    def setup_home(self, dt):
        """إعداد الشاشة الرئيسية"""
        self.update_welcome_message()
    
    def update_welcome_message(self):
        """تحديث رسالة الترحيب"""
        app = self.manager.app
        if app.user_data:
            name = app.user_data.get('name', 'عزيزي')
            self.ids.welcome_label.text = f"مرحباً {name}"
        else:
            self.ids.welcome_label.text = "مرحباً بك، يرجى تسجيل الدخول"
    
    def load_ads(self):
        """تحميل الإعلانات"""
        ads_container = self.ids.ads_container
        ads_container.clear_widgets()
        
        # إعلانات تجريبية
        ads = [
            ("خصم 20%", "استخدم كود QAT20", (0.2, 0.7, 0.3, 1)),
            ("توصيل مجاني", "للطلبات فوق 200 ريال", (0.3, 0.5, 0.8, 1)),
            ("قات مميز", "جودة عالية بسعر مناسب", (0.8, 0.6, 0.2, 1))
        ]
        
        for title, subtitle, color in ads:
            card = MDCard(
                orientation='vertical',
                size_hint=(None, None),
                size=(dp(100), dp(100)),
                elevation=1,
                radius=dp(10),
                md_bg_color=color
            )
            
            card.add_widget(MDLabel(
                text=title,
                theme_text_color="Custom",
                text_color=[1, 1, 1, 1],
                halign='center',
                font_name='DroidArabic',
                bold=True
            ))
            
            card.add_widget(MDLabel(
                text=subtitle,
                theme_text_color="Custom",
                text_color=[1, 1, 1, 0.8],
                halign='center',
                font_size='10sp',
                font_name='DroidArabic'
            ))
            
            ads_container.add_widget(card)
    
    def load_services(self):
        """تحميل الخدمات"""
        services_grid = self.ids.services_grid
        services_grid.clear_widgets()
        
        services = [
            ("المنتجات", "تصفح واشتري", "store", [0.2, 0.7, 0.3, 1]),
            ("طلباتي", "تتبع طلباتك", "clipboard-list", [0.3, 0.5, 0.8, 1]),
            ("المحفظة", "ادفع واشحن", "wallet", [0.8, 0.6, 0.2, 1]),
            ("التوصيل", "تتبع الطرود", "truck-delivery", [0.7, 0.3, 0.7, 1]),
            ("المغاسل", "غسل القات", "water", [0.2, 0.7, 0.7, 1]),
            ("الدعم", "مساعدة وسؤال", "headset", [0.8, 0.4, 0.2, 1])
        ]
        
        for title, subtitle, icon, color in services:
            card = HomeCard(
                title=ArabicSupport.arabic_text(title),
                subtitle=ArabicSupport.arabic_text(subtitle),
                icon=icon,
                icon_color=color
            )
            card.bind(on_release=lambda x, s=title.lower(): self.service_selected(s))
            services_grid.add_widget(card)
    
    def service_selected(self, service):
        """معالجة اختيار خدمة"""
        service_map = {
            'المنتجات': 'products',
            'طلباتي': 'orders',
            'المحفظة': 'wallet',
            'التوصيل': 'orders',
            'المغاسل': 'products',
            'الدعم': lambda: self.show_help()
        }
        
        action = service_map.get(service)
        if callable(action):
            action()
        elif action:
            self.manager.current = action
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        app = self.manager.app
        
        # تحديث عدد المنتجات
        app.api.get_products(
            filters={},
            success_callback=lambda res: self.on_products_loaded(res),
            error_callback=lambda err: self.ids.products_count.text = "المنتجات: 0"
        )
        
        # تحديث الرصيد
        if app.user_data:
            balance = app.user_data.get('wallet_balance', 0)
            self.ids.balance_label.text = f"الرصيد: {balance} ريال"
        
        # تحديث عدد الطلبات (محاكاة)
        self.ids.orders_count.text = "الطلبات: 3"
    
    def on_products_loaded(self, response):
        """عند تحميل المنتجات"""
        if response.get('success'):
            products = response.get('products', [])
            self.ids.products_count.text = f"المنتجات: {len(products)}"
    
    def show_notifications(self):
        """عرض الإشعارات"""
        app = self.manager.app
        if app.unread_notifications > 0:
            # فتح شاشة الإشعارات
            pass
        else:
            app.show_success("لا توجد إشعارات جديدة")
    
    def show_help(self):
        """عرض المساعدة"""
        app = self.manager.app
        app.show_help()
