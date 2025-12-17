# -*- coding: utf-8 -*-
"""
التطبيق الرئيسي - QatApp
تطبيق كامل مع دعم اللغة العربية
"""
import os
import json
from pathlib import Path

from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

# إعدادات قبل التحميل
Config.set('kivy', 'exit_on_escape', '0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# حجم النافذة للجوال
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.INTERNET, Permission.ACCESS_NETWORK_STATE])
else:
    Window.size = (360, 640)
    Window.clearcolor = (0.95, 0.95, 0.95, 1)

# استيراد الشاشات
from app.screens.login import LoginScreen
from app.screens.register import RegisterScreen
from app.screens.home import HomeScreen
from app.screens.products import ProductsScreen
from app.screens.cart import CartScreen
from app.screens.orders import OrdersScreen
from app.screens.wallet import WalletScreen
from app.screens.profile import ProfileScreen
from app.screens.admin import AdminDashboardScreen
from app.screens.seller import SellerDashboardScreen

from app.utils.arabic_support import ArabicSupport
from app.utils.api import API
from app.utils.notifications import NotificationManager

class MainApp(MDApp):
    """التطبيق الرئيسي"""
    
    # خصائص التطبيق
    user_data = ObjectProperty(None)
    user_token = StringProperty('')
    notifications = ListProperty([])
    unread_notifications = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Light"
        self.screen_manager = None
        self.nav_drawer = None
        self.api = API()
        self.notification_manager = NotificationManager()
        
        # إعداد دعم اللغة العربية
        ArabicSupport.setup_arabic_support()
    
    def build(self):
        """بناء التطبيق"""
        self.title = "تطبيق قات - بيع وتوصيل القات"
        
        # إنشاء مدير الشاشات
        self.screen_manager = ScreenManager()
        
        # إضافة الشاشات
        screens = [
            LoginScreen(name='login'),
            RegisterScreen(name='register'),
            HomeScreen(name='home'),
            ProductsScreen(name='products'),
            CartScreen(name='cart'),
            OrdersScreen(name='orders'),
            WalletScreen(name='wallet'),
            ProfileScreen(name='profile'),
            AdminDashboardScreen(name='admin_dashboard'),
            SellerDashboardScreen(name='seller_dashboard'),
        ]
        
        for screen in screens:
            screen.manager = self.screen_manager
            screen.manager.app = self
            self.screen_manager.add_widget(screen)
        
        # إنشاء قائمة التنقل
        self.create_navigation_drawer()
        
        # تحميل بيانات المستخدم إذا كان مسجل الدخول
        self.load_user_data()
        
        return self.screen_manager
    
    def create_navigation_drawer(self):
        """إنشاء قائمة التنقل الجانبية"""
        self.nav_drawer = MDNavigationDrawer(
            id="nav_drawer",
            radius=(0, 16, 16, 0),
        )
        
        # محتوى القائمة
        nav_content = MDList()
        
        # عناصر القائمة
        nav_items = [
            ("home", "الرئيسية", "home"),
            ("products", "المنتجات", "store"),
            ("cart", "سلة المشتريات", "cart"),
            ("orders", "طلباتي", "clipboard-list"),
            ("wallet", "المحفظة", "wallet"),
            ("profile", "الملف الشخصي", "account"),
            ("notifications", "الإشعارات", "bell"),
            ("settings", "الإعدادات", "cog"),
            ("help", "المساعدة", "help-circle"),
            ("logout", "تسجيل الخروج", "logout"),
        ]
        
        for screen_name, text, icon in nav_items:
            item = OneLineIconListItem(
                text=ArabicSupport.arabic_text(text),
                font_name='DroidArabic',
                on_release=lambda x, s=screen_name: self.nav_item_pressed(s)
            )
            item.add_widget(IconLeftWidget(icon=icon))
            nav_content.add_widget(item)
        
        self.nav_drawer.add_widget(nav_content)
    
    def nav_item_pressed(self, screen_name):
        """معالجة الضغط على عنصر في القائمة"""
        self.nav_drawer.set_state("close")
        
        if screen_name == 'logout':
            self.logout()
        elif screen_name == 'notifications':
            self.show_notifications()
        elif screen_name == 'settings':
            self.show_settings()
        elif screen_name == 'help':
            self.show_help()
        else:
            if hasattr(self.screen_manager, 'current'):
                self.screen_manager.current = screen_name
    
    def load_user_data(self):
        """تحميل بيانات المستخدم المحفوظة"""
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user_data.json')
            
            if store.exists('user'):
                self.user_data = store.get('user')
                self.user_token = store.get('token')
                
                # الانتقال للشاشة الرئيسية
                Clock.schedule_once(lambda dt: self.go_to_home(), 0.5)
        except:
            pass
    
    def save_user_data(self):
        """حفظ بيانات المستخدم"""
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user_data.json')
            
            if self.user_data:
                store.put('user', **self.user_data)
            if self.user_token:
                store.put('token', self.user_token)
        except:
            pass
    
    def logout(self):
        """تسجيل الخروج"""
        self.user_data = None
        self.user_token = ''
        self.notifications = []
        self.unread_notifications = 0
        
        # حذف البيانات المحفوظة
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user_data.json')
            store.clear()
        except:
            pass
        
        # العودة لشاشة تسجيل الدخول
        self.screen_manager.current = 'login'
        self.show_success("تم تسجيل الخروج بنجاح")
    
    def go_to_home(self):
        """الذهاب للشاشة الرئيسية"""
        if self.user_data:
            role = self.user_data.get('role', 'buyer')
            if role == 'admin':
                self.screen_manager.current = 'admin_dashboard'
            elif role == 'seller':
                self.screen_manager.current = 'seller_dashboard'
            else:
                self.screen_manager.current = 'home'
        else:
            self.screen_manager.current = 'login'
    
    def load_notifications(self):
        """تحميل الإشعارات"""
        if self.user_token:
            def on_success(response):
                if response.get('success'):
                    self.notifications = response.get('notifications', [])
                    self.unread_notifications = sum(1 for n in self.notifications if not n.get('is_read'))
            
            def on_error(error):
                pass
            
            self.api.get_notifications(self.user_token, on_success, on_error)
    
    def show_notifications(self):
        """عرض الإشعارات"""
        # سيتم تنفيذها في ملف منفصل
        pass
    
    def show_settings(self):
        """عرض الإعدادات"""
        # سيتم تنفيذها في ملف منفصل
        pass
    
    def show_help(self):
        """عرض المساعدة"""
        dialog = MDDialog(
            title="المساعدة والدعم",
            text=ArabicSupport.arabic_text("""
            تطبيق قات - منصة بيع وتوصيل القات
            
            للإستفسارات والدعم:
            📞 الهاتف: 771831482
            ✉️ البريد: support@qat-app.com
            
            أوقات العمل:
            من الأحد إلى الخميس
            9 صباحاً - 10 مساءً
            """),
            buttons=[
                MDFlatButton(
                    text="إغلاق",
                    font_name='DroidArabic',
                    on_press=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_error(self, message):
        """إظهار رسالة خطأ"""
        dialog = MDDialog(
            title="خطأ",
            text=ArabicSupport.arabic_text(message),
            buttons=[
                MDFlatButton(
                    text="حسناً",
                    font_name='DroidArabic',
                    on_press=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_success(self, message):
        """إظهار رسالة نجاح"""
        dialog = MDDialog(
            title="تم",
            text=ArabicSupport.arabic_text(message),
            buttons=[
                MDFlatButton(
                    text="حسناً",
                    font_name='DroidArabic',
                    on_press=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def on_pause(self):
        """عند إيقاف التطبيق مؤقتاً (للاندرويد)"""
        return True
    
    def on_resume(self):
        """عند استئناف التطبيق (للاندرويد)"""
        pass
    
    def on_stop(self):
        """عند إيقاف التطبيق"""
        self.save_user_data()
        return True

def run_app():
    """تشغيل التطبيق"""
    app = MainApp()
    app.run()

if __name__ == '__main__':
    run_app()
