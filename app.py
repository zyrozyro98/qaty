from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.image import Image
from kivy.uix.carousel import Carousel
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem, OneLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.chip import MDChip
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.tab import MDTabs
from kivymd.uix.imagelist import MDSmartTile
from kivymd.icon_definitions import md_icons
from kivy.network.urlrequest import UrlRequest
from kivy.storage.jsonstore import JsonStore
from datetime import datetime, timedelta
import json
import random
import string
import requests
from io import BytesIO
from PIL import Image as PILImage
import base64
import threading
import socketio
from functools import partial

# تكوين حجم النافذة لشاشة الجوال
Window.size = (400, 700)
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# API Configuration
API_BASE_URL = "https://qaty.onrender.com"
# API_BASE_URL = "http://localhost:5000"

# Socket.IO client
sio = socketio.Client()

class QatApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token = None
        self.user = None
        self.cart = []
        self.notifications = []
        self.current_market = None
        self.store = JsonStore('qat_app_data.json')
        self.load_from_storage()
        
        # Connect to Socket.IO
        self.connect_socketio()
    
    def connect_socketio(self):
        try:
            sio.connect(API_BASE_URL)
            print("Connected to Socket.IO server")
        except:
            print("Failed to connect to Socket.IO server")
    
    def load_from_storage(self):
        try:
            self.token = self.store.get('auth')['token'] if 'auth' in self.store else None
            self.user = self.store.get('auth')['user'] if 'auth' in self.store else None
            self.cart = self.store.get('cart')['items'] if 'cart' in self.store else []
        except:
            self.token = None
            self.user = None
            self.cart = []
    
    def save_to_storage(self):
        if self.token and self.user:
            self.store.put('auth', token=self.token, user=self.user)
        self.store.put('cart', items=self.cart)
    
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_hue = "700"
        
        self.screen_manager = ScreenManager()
        self.load_kv_string()
        
        # Add screens
        self.screen_manager.add_widget(SplashScreen(name='splash'))
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(RegisterScreen(name='register'))
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(ProductsScreen(name='products'))
        self.screen_manager.add_widget(CartScreen(name='cart'))
        self.screen_manager.add_widget(OrdersScreen(name='orders'))
        self.screen_manager.add_widget(WalletScreen(name='wallet'))
        self.screen_manager.add_widget(ProfileScreen(name='profile'))
        self.screen_manager.add_widget(SellerDashboardScreen(name='seller_dashboard'))
        self.screen_manager.add_widget(AdminDashboardScreen(name='admin_dashboard'))
        
        # Check if user is already logged in
        if self.token and self.user:
            self.screen_manager.current = 'home'
            # Start listening for notifications
            self.start_notification_listener()
        else:
            self.screen_manager.current = 'splash'
            Clock.schedule_once(lambda dt: setattr(self.screen_manager, 'current', 'login'), 2)
        
        return self.screen_manager
    
    def start_notification_listener(self):
        # Listen for socket notifications
        if self.user:
            @sio.on(f'notification_{self.user["id"]}')
            def on_notification(data):
                self.notifications.append(data)
                self.show_notification(data['title'], data['message'])
    
    def show_notification(self, title, message):
        Snackbar(
            text=f"{title}: {message}",
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(Window.width - 20) / Window.width,
            bg_color=(0.2, 0.7, 0.3, 1)
        ).open()
    
    def show_error(self, message):
        Snackbar(
            text=message,
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(Window.width - 20) / Window.width,
            bg_color=(0.9, 0.2, 0.2, 1)
        ).open()
    
    def api_request(self, endpoint, method='GET', data=None, callback=None, error_callback=None):
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        url = f"{API_BASE_URL}{endpoint}"
        
        def on_success(req, result):
            if callback:
                callback(result)
        
        def on_error(req, error):
            if error_callback:
                error_callback(error)
            else:
                self.show_error("حدث خطأ في الاتصال بالخادم")
        
        if method == 'GET':
            UrlRequest(url, req_headers=headers, on_success=on_success, on_error=on_error)
        elif method == 'POST':
            UrlRequest(url, req_headers=headers, req_body=json.dumps(data) if data else None,
                      on_success=on_success, on_error=on_error, method='POST',
                      headers={'Content-Type': 'application/json'})
        elif method == 'PUT':
            UrlRequest(url, req_headers=headers, req_body=json.dumps(data) if data else None,
                      on_success=on_success, on_error=on_error, method='PUT',
                      headers={'Content-Type': 'application/json'})
    
    def login(self, email, password):
        def on_success(result):
            if result.get('status') == 'success':
                self.token = result['token']
                self.user = result['user']
                self.save_to_storage()
                self.screen_manager.current = 'home'
                self.start_notification_listener()
                self.show_notification("مرحباً بك", f"تم تسجيل الدخول بنجاح")
            else:
                self.show_error(result.get('message', 'حدث خطأ'))
        
        self.api_request('/api/login', 'POST', {'email': email, 'password': password}, on_success)
    
    def register(self, user_data):
        def on_success(result):
            if result.get('status') == 'success':
                self.token = result['token']
                self.user = result['user']
                self.save_to_storage()
                self.screen_manager.current = 'home'
                self.start_notification_listener()
                self.show_notification("مرحباً بك", "تم إنشاء الحساب بنجاح")
            else:
                self.show_error(result.get('message', 'حدث خطأ'))
        
        self.api_request('/api/register', 'POST', user_data, on_success)
    
    def logout(self):
        self.token = None
        self.user = None
        self.cart = []
        self.save_to_storage()
        self.screen_manager.current = 'login'
    
    def add_to_cart(self, product, quantity=1, washing=False):
        for item in self.cart:
            if item['product']['id'] == product['id']:
                item['quantity'] += quantity
                item['washing'] = washing
                break
        else:
            self.cart.append({
                'product': product,
                'quantity': quantity,
                'washing': washing
            })
        
        self.save_to_storage()
        self.show_notification("تم الإضافة", f"تم إضافة {product['name']} إلى السلة")
    
    def remove_from_cart(self, product_id):
        self.cart = [item for item in self.cart if item['product']['id'] != product_id]
        self.save_to_storage()
    
    def get_cart_total(self):
        total = 0
        for item in self.cart:
            item_total = item['product']['price'] * item['quantity']
            if item.get('washing', False):
                item_total += 100  # Washing price
            total += item_total
        return total
    
    def create_order(self, delivery_address, payment_method):
        if not self.user:
            self.show_error("يرجى تسجيل الدخول أولاً")
            return
        
        items = []
        for item in self.cart:
            items.append({
                'product_id': item['product']['id'],
                'quantity': item['quantity'],
                'washing': item.get('washing', False)
            })
        
        order_data = {
            'items': items,
            'delivery_address': delivery_address,
            'payment_method': payment_method,
            'market_id': self.current_market['id'] if self.current_market else ''
        }
        
        def on_success(result):
            if result.get('status') == 'success':
                self.cart = []
                self.save_to_storage()
                self.screen_manager.current = 'orders'
                self.show_notification("نجاح", "تم إنشاء الطلب بنجاح")
                
                # Refresh orders screen
                orders_screen = self.screen_manager.get_screen('orders')
                orders_screen.load_orders()
            else:
                self.show_error(result.get('message', 'حدث خطأ'))
        
        self.api_request('/api/orders', 'POST', order_data, on_success)
    
    def topup_wallet(self, amount, method, reference):
        def on_success(result):
            if result.get('status') == 'success':
                self.show_notification("نجاح", result['message'])
                # Refresh wallet screen
                wallet_screen = self.screen_manager.get_screen('wallet')
                wallet_screen.load_wallet()
            else:
                self.show_error(result.get('message', 'حدث خطأ'))
        
        data = {
            'amount': amount,
            'method': method,
            'reference': reference
        }
        
        self.api_request('/api/wallet/topup', 'POST', data, on_success)
    
    def load_kv_string(self):
        Builder.load_string('''
<SplashScreen>:
    MDFloatLayout:
        md_bg_color: app.theme_cls.primary_color
        Image:
            source: 'assets/logo.png' if os.path.exists('assets/logo.png') else ''
            size_hint: None, None
            size: 200, 200
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}
        MDLabel:
            text: 'تطبيق قات'
            font_style: 'H2'
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: 1, 1, 1, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
        MDSpinner:
            size_hint: None, None
            size: dp(46), dp(46)
            pos_hint: {'center_x': 0.5, 'center_y': 0.2}
            active: True

<LoginScreen>:
    name: 'login'
    
    MDFloatLayout:
        md_bg_color: app.theme_cls.bg_normal
        
        MDTopAppBar:
            title: "تسجيل الدخول"
            elevation: 0
            pos_hint: {'top': 1}
            md_bg_color: app.theme_cls.primary_color
        
        ScrollView:
            pos_hint: {'top': 0.95, 'center_x': 0.5}
            size_hint: 1, 0.9
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(20)
                padding: dp(30)
                size_hint_y: None
                height: self.minimum_height
                pos_hint: {'center_y': 0.5}
                
                MDLabel:
                    text: "مرحباً بك في تطبيق قات"
                    font_style: 'H4'
                    halign: 'center'
                    size_hint_y: None
                    height: dp(50)
                
                MDTextField:
                    id: email_input
                    hint_text: "البريد الإلكتروني"
                    icon_right: "email"
                    mode: "rectangle"
                    size_hint_y: None
                    height: dp(60)
                    font_size: '16sp'
                
                MDTextField:
                    id: password_input
                    hint_text: "كلمة المرور"
                    icon_right: "lock"
                    mode: "rectangle"
                    password: True
                    size_hint_y: None
                    height: dp(60)
                    font_size: '16sp'
                
                MDRaisedButton:
                    text: "تسجيل الدخول"
                    size_hint_y: None
                    height: dp(50)
                    font_size: '16sp'
                    on_release: root.login()
                
                MDLabel:
                    text: "أو"
                    halign: 'center'
                    size_hint_y: None
                    height: dp(30)
                
                MDFlatButton:
                    text: "إنشاء حساب جديد"
                    size_hint_y: None
                    height: dp(40)
                    font_size: '16sp'
                    on_release: root.go_to_register()

<RegisterScreen>:
    name: 'register'
    
    MDFloatLayout:
        md_bg_color: app.theme_cls.bg_normal
        
        MDTopAppBar:
            title: "إنشاء حساب جديد"
            elevation: 0
            left_action_items: [['arrow-left', lambda x: root.go_to_login()]]
            pos_hint: {'top': 1}
            md_bg_color: app.theme_cls.primary_color
        
        ScrollView:
            pos_hint: {'top': 0.95, 'center_x': 0.5}
            size_hint: 1, 0.9
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(15)
                padding: dp(20)
                size_hint_y: None
                height: self.minimum_height
                
                MDTextField:
                    id: name_input
                    hint_text: "الاسم الكامل"
                    icon_right: "account"
                    mode: "rectangle"
                    size_hint_y: None
                    height: dp(60)
                
                MDTextField:
                    id: email_input
                    hint_text: "البريد الإلكتروني"
                    icon_right: "email"
                    mode: "rectangle"
                    size_hint_y: None
                    height: dp(60)
                
                MDTextField:
                    id: phone_input
                    hint_text: "رقم الهاتف"
                    icon_right: "phone"
                    mode: "rectangle"
                    size_hint_y: None
                    height: dp(60)
                
                MDTextField:
                    id: password_input
                    hint_text: "كلمة المرور"
                    icon_right: "lock"
                    mode: "rectangle"
                    password: True
                    size_hint_y: None
                    height: dp(60)
                
                MDTextField:
                    id: confirm_password_input
                    hint_text: "تأكيد كلمة المرور"
                    icon_right: "lock-check"
                    mode: "rectangle"
                    password: True
                    size_hint_y: None
                    height: dp(60)
                
                MDLabel:
                    text: "نوع المستخدم:"
                    size_hint_y: None
                    height: dp(30)
                
                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(50)
                    
                    MDCheckbox:
                        id: buyer_check
                        group: 'user_type'
                        active: True
                        size_hint: None, None
                        size: dp(30), dp(30)
                    
                    MDLabel:
                        text: "مشتري"
                        size_hint_x: 0.3
                    
                    MDCheckbox:
                        id: seller_check
                        group: 'user_type'
                        size_hint: None, None
                        size: dp(30), dp(30)
                    
                    MDLabel:
                        text: "بائع"
                        size_hint_x: 0.3
                    
                    MDCheckbox:
                        id: driver_check
                        group: 'user_type'
                        size_hint: None, None
                        size: dp(30), dp(30)
                    
                    MDLabel:
                        text: "مندوب توصيل"
                        size_hint_x: 0.4
                
                MDTextField:
                    id: store_name_input
                    hint_text: "اسم المتجر (للبائعين)"
                    icon_right: "store"
                    mode: "rectangle"
                    size_hint_y: None
                    height: dp(60)
                    opacity: 0
                    disabled: True
                
                MDTextField:
                    id: vehicle_input
                    hint_text: "نوع المركبة (للمندوبين)"
                    icon_right: "car"
                    mode: "rectangle"
                    size_hint_y: None
                    height: dp(60)
                    opacity: 0
                    disabled: True
                
                MDRaisedButton:
                    text: "إنشاء الحساب"
                    size_hint_y: None
                    height: dp(50)
                    on_release: root.register()

<HomeScreen>:
    name: 'home'
    
    MDNavigationLayout:
        x: toolbar.height
        
        MDNavigationDrawer:
            id: nav_drawer
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(10)
                
                MDLabel:
                    text: "تطبيق قات"
                    font_style: 'H5'
                    size_hint_y: None
                    height: dp(50)
                    halign: 'center'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(10)
                    
                    OneLineAvatarIconListItem:
                        text: "الرئيسية"
                        IconLeftWidget:
                            icon: "home"
                        on_release: root.nav_to('home')
                    
                    OneLineAvatarIconListItem:
                        text: "المنتجات"
                        IconLeftWidget:
                            icon: "shopping"
                        on_release: root.nav_to('products')
                    
                    OneLineAvatarIconListItem:
                        text: "طلباتي"
                        IconLeftWidget:
                            icon: "package-variant"
                        on_release: root.nav_to('orders')
                    
                    OneLineAvatarIconListItem:
                        text: "المحفظة"
                        IconLeftWidget:
                            icon: "wallet"
                        on_release: root.nav_to('wallet')
                    
                    OneLineAvatarIconListItem:
                        text: "الملف الشخصي"
                        IconLeftWidget:
                            icon: "account"
                        on_release: root.nav_to('profile')
                    
                    OneLineAvatarIconListItem:
                        text: "لوحة البائعين"
                        IconLeftWidget:
                            icon: "store"
                        on_release: root.nav_to('seller_dashboard')
                    
                    OneLineAvatarIconListItem:
                        text: "لوحة المدير"
                        IconLeftWidget:
                            icon: "shield-account"
                        on_release: root.nav_to('admin_dashboard')
                    
                    OneLineAvatarIconListItem:
                        text: "تسجيل الخروج"
                        IconLeftWidget:
                            icon: "logout"
                        on_release: root.logout()
        
        MDFloatLayout:
            MDTopAppBar:
                id: toolbar
                title: "الرئيسية"
                elevation: 0
                left_action_items: [['menu', lambda x: nav_drawer.set_state("open")]]
                right_action_items: [['bell', root.show_notifications]]
                pos_hint: {'top': 1}
                md_bg_color: app.theme_cls.primary_color
            
            ScrollView:
                pos_hint: {'top': 0.95, 'center_x': 0.5}
                size_hint: 1, 0.9
                
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(20)
                    padding: dp(20)
                    size_hint_y: None
                    height: self.minimum_height
                    
                    MDCard:
                        orientation: 'vertical'
                        padding: dp(20)
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(120)
                        
                        MDLabel:
                            text: f"مرحباً بك، {app.user['name'] if app.user else 'زائر'}"
                            font_style: 'H5'
                            theme_text_color: 'Primary'
                        
                        MDLabel:
                            text: "منصة شاملة لبيع وتوصيل القات"
                            font_style: 'Body1'
                            theme_text_color: 'Secondary'
                    
                    MDLabel:
                        text: "الإحصائيات السريعة"
                        font_style: 'H6'
                        size_hint_y: None
                        height: dp(40)
                    
                    MDGridLayout:
                        cols: 2
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(200)
                        
                        MDCard:
                            orientation: 'vertical'
                            padding: dp(15)
                            spacing: dp(10)
                            
                            MDLabel:
                                text: "السلة"
                                font_style: 'Body2'
                                theme_text_color: 'Secondary'
                                halign: 'center'
                            
                            MDLabel:
                                id: cart_count_label
                                text: "0"
                                font_style: 'H4'
                                halign: 'center'
                                theme_text_color: 'Primary'
                        
                        MDCard:
                            orientation: 'vertical'
                            padding: dp(15)
                            spacing: dp(10)
                            
                            MDLabel:
                                text: "طلباتي"
                                font_style: 'Body2'
                                theme_text_color: 'Secondary'
                                halign: 'center'
                            
                            MDLabel:
                                id: orders_count_label
                                text: "0"
                                font_style: 'H4'
                                halign: 'center'
                                theme_text_color: 'Primary'
                        
                        MDCard:
                            orientation: 'vertical'
                            padding: dp(15)
                            spacing: dp(10)
                            
                            MDLabel:
                                text: "الإشعارات"
                                font_style: 'Body2'
                                theme_text_color: 'Secondary'
                                halign: 'center'
                            
                            MDLabel:
                                id: notifications_count_label
                                text: "0"
                                font_style: 'H4'
                                halign: 'center'
                                theme_text_color: 'Primary'
                        
                        MDCard:
                            orientation: 'vertical'
                            padding: dp(15)
                            spacing: dp(10)
                            
                            MDLabel:
                                text: "الرصيد"
                                font_style: 'Body2'
                                theme_text_color: 'Secondary'
                                halign: 'center'
                            
                            MDLabel:
                                id: balance_label
                                text: "0 ريال"
                                font_style: 'H4'
                                halign: 'center'
                                theme_text_color: 'Primary'
                    
                    MDLabel:
                        text: "الأسواق المتاحة"
                        font_style: 'H6'
                        size_hint_y: None
                        height: dp(40)
                    
                    ScrollView:
                        size_hint_y: None
                        height: dp(150)
                        
                        MDBoxLayout:
                            id: markets_container
                            orientation: 'horizontal'
                            spacing: dp(10)
                            size_hint_x: None
                            width: self.minimum_width
                            padding: dp(10)
                    
                    MDLabel:
                        text: "الإعلانات"
                        font_style: 'H6'
                        size_hint_y: None
                        height: dp(40)
                    
                    Carousel:
                        id: ads_carousel
                        size_hint_y: None
                        height: dp(200)
                        loop: True

<ProductsScreen>:
    name: 'products'
    
    MDFloatLayout:
        MDTopAppBar:
            title: "المنتجات"
            elevation: 0
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            right_action_items: [['cart', lambda x: root.go_to_cart()]]
            pos_hint: {'top': 1}
            md_bg_color: app.theme_cls.primary_color
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            padding: dp(10)
            pos_hint: {'top': 0.95}
            size_hint_y: 0.95
            
            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(10)
                size_hint_y: None
                height: dp(50)
                
                MDTextField:
                    id: search_input
                    hint_text: "بحث في المنتجات..."
                    mode: "rectangle"
                    size_hint_x: 0.7
                
                MDIconButton:
                    icon: "filter"
                    on_release: root.show_filters()
            
            MDTabs:
                id: tabs
                on_tab_switch: root.on_tab_switch(*args)
            
            ScrollView:
                id: products_scroll
                
                MDGridLayout:
                    id: products_container
                    cols: 2
                    spacing: dp(15)
                    padding: dp(15)
                    size_hint_y: None
                    height: self.minimum_height
                    adaptive_height: True

<ProductCard@MDCard>:
    orientation: 'vertical'
    size_hint: None, None
    size: dp(160), dp(240)
    padding: dp(10)
    spacing: dp(5)
    
    Image:
        id: product_image
        source: ''
        size_hint_y: None
        height: dp(100)
        allow_stretch: True
    
    MDLabel:
        id: product_name
        text: ''
        font_style: 'Body2'
        size_hint_y: None
        height: dp(40)
        halign: 'center'
        shorten: True
    
    MDLabel:
        id: product_price
        text: ''
        font_style: 'H6'
        theme_text_color: 'Primary'
        size_hint_y: None
        height: dp(30)
        halign: 'center'
    
    MDRaisedButton:
        text: "إضافة للسلة"
        size_hint_y: None
        height: dp(30)
        on_release: app.root.get_screen('products').add_to_cart(root.product_data)

<CartScreen>:
    name: 'cart'
    
    MDFloatLayout:
        MDTopAppBar:
            title: "سلة التسوق"
            elevation: 0
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            pos_hint: {'top': 1}
            md_bg_color: app.theme_cls.primary_color
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            padding: dp(10)
            pos_hint: {'top': 0.95}
            size_hint_y: 0.95
            
            MDLabel:
                id: empty_label
                text: "السلة فارغة"
                font_style: 'H5'
                halign: 'center'
                theme_text_color: 'Secondary'
                size_hint_y: None
                height: dp(100)
                opacity: 0
            
            ScrollView:
                id: cart_scroll
                
                MDBoxLayout:
                    id: cart_container
                    orientation: 'vertical'
                    spacing: dp(15)
                    padding: dp(15)
                    size_hint_y: None
                    height: self.minimum_height
                    adaptive_height: True
            
            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(10)
                size_hint_y: None
                height: dp(80)
                padding: dp(10)
                
                MDLabel:
                    id: total_label
                    text: "المجموع: 0 ريال"
                    font_style: 'H6'
                    theme_text_color: 'Primary'
                    halign: 'right'
                    size_hint_x: 0.6
                
                MDRaisedButton:
                    id: checkout_btn
                    text: "إتمام الشراء"
                    size_hint_x: 0.4
                    disabled: True
                    on_release: root.checkout()

<CartItemCard@MDCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(120)
    padding: dp(10)
    spacing: dp(10)
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(5)
        size_hint_x: 0.7
        
        MDLabel:
            id: item_name
            text: ''
            font_style: 'Body1'
            size_hint_y: None
            height: dp(30)
        
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(10)
            size_hint_y: None
            height: dp(30)
            
            MDLabel:
                id: item_price
                text: ''
                font_style: 'Body2'
                theme_text_color: 'Secondary'
            
            MDLabel:
                text: "×"
                font_style: 'Body2'
                theme_text_color: 'Secondary'
            
            MDLabel:
                id: item_quantity
                text: ''
                font_style: 'Body2'
                theme_text_color: 'Secondary'
        
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(10)
            size_hint_y: None
            height: dp(30)
            
            MDCheckbox:
                id: washing_check
                size_hint: None, None
                size: dp(20), dp(20)
                on_active: root.toggle_washing()
            
            MDLabel:
                text: "غسيل القات (+100 ريال)"
                font_style: 'Caption'
                theme_text_color: 'Secondary'
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(5)
        size_hint_x: 0.3
        
        MDIconButton:
            icon: "delete"
            theme_text_color: 'Error'
            on_release: root.remove_item()
        
        MDLabel:
            id: item_total
            text: ''
            font_style: 'H6'
            theme_text_color: 'Primary'
            halign: 'center'

<OrdersScreen>:
    name: 'orders'
    
    MDFloatLayout:
        MDTopAppBar:
            title: "طلباتي"
            elevation: 0
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            right_action_items: [['plus', lambda x: root.new_order()]]
            pos_hint: {'top': 1}
            md_bg_color: app.theme_cls.primary_color
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            padding: dp(10)
            pos_hint: {'top': 0.95}
            size_hint_y: 0.95
            
            MDTabs:
                id: order_tabs
                
                MDTab:
                    text: "الطلبات الجارية"
                    
                    ScrollView:
                        
                        MDBoxLayout:
                            id: active_orders_container
                            orientation: 'vertical'
                            spacing: dp(15)
                            padding: dp(15)
                            size_hint_y: None
                            height: self.minimum_height
                            adaptive_height: True
                
                MDTab:
                    text: "الطلبات السابقة"
                    
                    ScrollView:
                        
                        MDBoxLayout:
                            id: past_orders_container
                            orientation: 'vertical'
                            spacing: dp(15)
                            padding: dp(15)
                            size_hint_y: None
                            height: self.minimum_height
                            adaptive_height: True

<OrderCard@MDCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(180)
    padding: dp(15)
    spacing: dp(10)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        
        MDLabel:
            id: order_code
            text: ''
            font_style: 'H6'
            theme_text_color: 'Primary'
            size_hint_x: 0.6
        
        MDLabel:
            id: order_status
            text: ''
            font_style: 'Body2'
            theme_text_color: 'Custom'
            text_color: 0, 0.5, 0, 1
            size_hint_x: 0.4
    
    MDLabel:
        id: order_items
        text: ''
        font_style: 'Body2'
        theme_text_color: 'Secondary'
        size_hint_y: None
        height: dp(40)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        
        MDLabel:
            id: order_total
            text: ''
            font_style: 'Body1'
            theme_text_color: 'Primary'
        
        MDLabel:
            id: order_date
            text: ''
            font_style: 'Caption'
            theme_text_color: 'Secondary'
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        
        MDRaisedButton:
            text: "تفاصيل"
            size_hint_x: 0.5
            on_release: root.show_details()
        
        MDFlatButton:
            text: "تتبع"
            size_hint_x: 0.5
            on_release: root.track_order()

<WalletScreen>:
    name: 'wallet'
    
    MDFloatLayout:
        MDTopAppBar:
            title: "المحفظة"
            elevation: 0
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            right_action_items: [['plus', lambda x: root.show_topup_dialog()]]
            pos_hint: {'top': 1}
            md_bg_color: app.theme_cls.primary_color
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(20)
            padding: dp(20)
            pos_hint: {'top': 0.95}
            size_hint_y: 0.95
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                size_hint_y: None
                height: dp(150)
                
                MDLabel:
                    text: "الرصيد المتاح"
                    font_style: 'Body1'
                    theme_text_color: 'Secondary'
                    halign: 'center'
                
                MDLabel:
                    id: balance_label
                    text: "0 ريال"
                    font_style: 'H2'
                    halign: 'center'
                    theme_text_color: 'Primary'
                
                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(40)
                    
                    MDRaisedButton:
                        text: "شحن الرصيد"
                        size_hint_x: 0.5
                        on_release: root.show_topup_dialog()
                    
                    MDFlatButton:
                        text: "سحب الرصيد"
                        size_hint_x: 0.5
                        on_release: root.show_withdraw_dialog()
            
            MDLabel:
                text: "المحافظ الإلكترونية"
                font_style: 'H6'
                size_hint_y: None
                height: dp(40)
            
            ScrollView:
                
                MDBoxLayout:
                    id: wallets_container
                    orientation: 'vertical'
                    spacing: dp(15)
                    padding: dp(10)
                    size_hint_y: None
                    height: self.minimum_height
                    adaptive_height: True
            
            MDLabel:
                text: "آخر العمليات"
                font_style: 'H6'
                size_hint_y: None
                height: dp(40)
            
            ScrollView:
                size_hint_y: 0.4
                
                MDBoxLayout:
                    id: transactions_container
                    orientation: 'vertical'
                    spacing: dp(10)
                    padding: dp(10)
                    size_hint_y: None
                    height: self.minimum_height
                    adaptive_height: True

<WalletCard@MDCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(80)
    padding: dp(15)
    spacing: dp(10)
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(5)
        size_hint_x: 0.7
        
        MDLabel:
            id: wallet_name
            text: ''
            font_style: 'Body1'
            size_hint_y: None
            height: dp(30)
        
        MDLabel:
            id: wallet_balance
            text: ''
            font_style: 'Body2'
            theme_text_color: 'Secondary'
            size_hint_y: None
            height: dp(30)
    
    MDRaisedButton:
        text: "شحن"
        size_hint_x: 0.3
        on_release: root.topup()

<TransactionCard@MDCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(70)
    padding: dp(10)
    spacing: dp(10)
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(5)
        size_hint_x: 0.7
        
        MDLabel:
            id: trans_desc
            text: ''
            font_style: 'Body2'
            size_hint_y: None
            height: dp(25)
        
        MDLabel:
            id: trans_date
            text: ''
            font_style: 'Caption'
            theme_text_color: 'Secondary'
            size_hint_y: None
            height: dp(20)
    
    MDLabel:
        id: trans_amount
        text: ''
        font_style: 'Body1'
        theme_text_color: 'Custom'
        text_color: 0, 0.5, 0, 1
        size_hint_x: 0.3
        halign: 'right'

<ProfileScreen>:
    name: 'profile'
    
    MDFloatLayout:
        MDTopAppBar:
            title: "الملف الشخصي"
            elevation: 0
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            right_action_items: [['pencil', lambda x: root.edit_profile()]]
            pos_hint: {'top': 1}
            md_bg_color: app.theme_cls.primary_color
        
        ScrollView:
            pos_hint: {'top': 0.95, 'center_x': 0.5}
            size_hint: 1, 0.9
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(20)
                padding: dp(20)
                size_hint_y: None
                height: self.minimum_height
                
                MDCard:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(200)
                    
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(15)
                        size_hint_y: None
                        height: dp(80)
                        
                        Image:
                            id: profile_image
                            source: ''
                            size_hint: None, None
                            size: dp(80), dp(80)
                            radius: [dp(40),]
                        
                        MDBoxLayout:
                            orientation: 'vertical'
                            spacing: dp(5)
                            
                            MDLabel:
                                id: profile_name
                                text: ''
                                font_style: 'H5'
                                theme_text_color: 'Primary'
                            
                            MDLabel:
                                id: profile_email
                                text: ''
                                font_style: 'Body2'
                                theme_text_color: 'Secondary'
                    
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(30)
                        
                        MDLabel:
                            text: "رقم الهاتف:"
                            font_style: 'Body2'
                            theme_text_color: 'Secondary'
                        
                        MDLabel:
                            id: profile_phone
                            text: ''
                            font_style: 'Body2'
                            theme_text_color: 'Primary'
                    
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(30)
                        
                        MDLabel:
                            text: "نوع المستخدم:"
                            font_style: 'Body2'
                            theme_text_color: 'Secondary'
                        
                        MDLabel:
                            id: profile_type
                            text: ''
                            font_style: 'Body2'
                            theme_text_color: 'Primary'
                
                MDLabel:
                    text: "الإحصائيات"
                    font_style: 'H6'
                    size_hint_y: None
                    height: dp(40)
                
                MDGridLayout:
                    cols: 2
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(200)
                    
                    MDCard:
                        orientation: 'vertical'
                        padding: dp(15)
                        spacing: dp(10)
                        
                        MDLabel:
                            text: "عدد الطلبات"
                            font_style: 'Body2'
                            theme_text_color: 'Secondary'
                            halign: 'center'
                        
                        MDLabel:
                            id: orders_count
                            text: "0"
                            font_style: 'H4'
                            halign: 'center'
                            theme_text_color: 'Primary'
                    
                    MDCard:
                        orientation: 'vertical'
                        padding: dp(15)
                        spacing: dp(10)
                        
                        MDLabel:
                            text: "إجمالي المشتريات"
                            font_style: 'Body2'
                            theme_text_color: 'Secondary'
                            halign: 'center'
                        
                        MDLabel:
                            id: total_spent
                            text: "0 ريال"
                            font_style: 'H4'
                            halign: 'center'
                            theme_text_color: 'Primary'
                    
                    MDCard:
                        orientation: 'vertical'
                        padding: dp(15)
                        spacing: dp(10)
                        
                        MDLabel:
                            text: "التقييم"
                            font_style: 'Body2'
                            theme_text_color: 'Secondary'
                            halign: 'center'
                        
                        MDLabel:
                            id: user_rating
                            text: "0.0"
                            font_style: 'H4'
                            halign: 'center'
                            theme_text_color: 'Primary'
                    
                    MDCard:
                        orientation: 'vertical'
                        padding: dp(15)
                        spacing: dp(10)
                        
                        MDLabel:
                            text: "تاريخ الانضمام"
                            font_style: 'Body2'
                            theme_text_color: 'Secondary'
                            halign: 'center'
                        
                        MDLabel:
                            id: join_date
                            text: ''
                            font_style: 'Caption'
                            halign: 'center'
                            theme_text_color: 'Primary'
                
                MDRaisedButton:
                    text: "تسجيل الخروج"
                    size_hint_y: None
                    height: dp(50)
                    on_release: root.logout()

<SellerDashboardScreen>:
    name: 'seller_dashboard'
    
    MDFloatLayout:
        MDTopAppBar:
            title: "لوحة البائعين"
            elevation: 0
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            pos_hint: {'top': 1}
            md_bg_color: app.theme_cls.primary_color
        
        MDTabs:
            pos_hint: {'top': 0.95}
            size_hint_y: 0.95
            
            MDTab:
                text: "منتجاتي"
                
                MDFloatLayout:
                    
                    MDRaisedButton:
                        text: "إضافة منتج جديد"
                        pos_hint: {'top': 0.95, 'right': 0.95}
                        size_hint: None, None
                        size: dp(150), dp(40)
                        on_release: root.add_product()
                    
                    ScrollView:
                        pos_hint: {'top': 0.9, 'center_x': 0.5}
                        size_hint: 1, 0.9
                        
                        MDBoxLayout:
                            id: seller_products_container
                            orientation: 'vertical'
                            spacing: dp(15)
                            padding: dp(15)
                            size_hint_y: None
                            height: self.minimum_height
                            adaptive_height: True
            
            MDTab:
                text: "طلباتي"
                
                ScrollView:
                    
                    MDBoxLayout:
                        id: seller_orders_container
                        orientation: 'vertical'
                        spacing: dp(15)
                        padding: dp(15)
                        size_hint_y: None
                        height: self.minimum_height
                        adaptive_height: True
            
            MDTab:
                text: "الإحصاءات"
                
                ScrollView:
                    
                    MDBoxLayout:
                        orientation: 'vertical'
                        spacing: dp(20)
                        padding: dp(20)
                        size_hint_y: None
                        height: self.minimum_height
                        
                        MDCard:
                            orientation: 'vertical'
                            padding: dp(20)
                            spacing: dp(10)
                            size_hint_y: None
                            height: dp(150)
                            
                            MDLabel:
                                text: "إجمالي المبيعات"
                                font_style: 'H6'
                                theme_text_color: 'Secondary'
                                halign: 'center'
                            
                            MDLabel:
                                id: total_sales
                                text: "0 ريال"
                                font_style: 'H2'
                                halign: 'center'
                                theme_text_color: 'Primary'
                        
                        MDGridLayout:
                            cols: 2
                            spacing: dp(10)
                            size_hint_y: None
                            height: dp(200)
                            
                            MDCard:
                                orientation: 'vertical'
                                padding: dp(15)
                                spacing: dp(10)
                                
                                MDLabel:
                                    text: "عدد المنتجات"
                                    font_style: 'Body2'
                                    theme_text_color: 'Secondary'
                                    halign: 'center'
                                
                                MDLabel:
                                    id: products_count
                                    text: "0"
                                    font_style: 'H4'
                                    halign: 'center'
                                    theme_text_color: 'Primary'
                            
                            MDCard:
                                orientation: 'vertical'
                                padding: dp(15)
                                spacing: dp(10)
                                
                                MDLabel:
                                    text: "عدد الطلبات"
                                    font_style: 'Body2'
                                    theme_text_color: 'Secondary'
                                    halign: 'center'
                                
                                MDLabel:
                                    id: seller_orders_count
                                    text: "0"
                                    font_style: 'H4'
                                    halign: 'center'
                                    theme_text_color: 'Primary'
                            
                            MDCard:
                                orientation: 'vertical'
                                padding: dp(15)
                                spacing: dp(10)
                                
                                MDLabel:
                                    text: "التقييم العام"
                                    font_style: 'Body2'
                                    theme_text_color: 'Secondary'
                                    halign: 'center'
                                
                                MDLabel:
                                    id: seller_rating
                                    text: "0.0"
                                    font_style: 'H4'
                                    halign: 'center'
                                    theme_text_color: 'Primary'
                            
                            MDCard:
                                orientation: 'vertical'
                                padding: dp(15)
                                spacing: dp(10)
                                
                                MDLabel:
                                    text: "الرصيد المتاح"
                                    font_style: 'Body2'
                                    theme_text_color: 'Secondary'
                                    halign: 'center'
                                
                                MDLabel:
                                    id: seller_balance
                                    text: "0 ريال"
                                    font_style: 'H4'
                                    halign: 'center'
                                    theme_text_color: 'Primary'

<AdminDashboardScreen>:
    name: 'admin_dashboard'
    
    MDFloatLayout:
        MDTopAppBar:
            title: "لوحة المدير"
            elevation: 0
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            pos_hint: {'top': 1}
            md_bg_color: app.theme_cls.primary_color
        
        MDTabs:
            pos_hint: {'top': 0.95}
            size_hint_y: 0.95
            
            MDTab:
                text: "المستخدمين"
                
                MDFloatLayout:
                    
                    MDRaisedButton:
                        text: "إضافة مستخدم"
                        pos_hint: {'top': 0.95, 'right': 0.95}
                        size_hint: None, None
                        size: dp(150), dp(40)
                        on_release: root.add_user()
                    
                    ScrollView:
                        pos_hint: {'top': 0.9, 'center_x': 0.5}
                        size_hint: 1, 0.9
                        
                        MDBoxLayout:
                            id: users_container
                            orientation: 'vertical'
                            spacing: dp(15)
                            padding: dp(15)
                            size_hint_y: None
                            height: self.minimum_height
                            adaptive_height: True
            
            MDTab:
                text: "الأسواق"
                
                MDFloatLayout:
                    
                    MDRaisedButton:
                        text: "إضافة سوق"
                        pos_hint: {'top': 0.95, 'right': 0.95}
                        size_hint: None, None
                        size: dp(150), dp(40)
                        on_release: root.add_market()
                    
                    ScrollView:
                        pos_hint: {'top': 0.9, 'center_x': 0.5}
                        size_hint: 1, 0.9
                        
                        MDBoxLayout:
                            id: markets_admin_container
                            orientation: 'vertical'
                            spacing: dp(15)
                            padding: dp(15)
                            size_hint_y: None
                            height: self.minimum_height
                            adaptive_height: True
            
            MDTab:
                text: "المندوبين"
                
                MDFloatLayout:
                    
                    MDRaisedButton:
                        text: "إضافة مندوب"
                        pos_hint: {'top': 0.95, 'right': 0.95}
                        size_hint: None, None
                        size: dp(150), dp(40)
                        on_release: root.add_driver()
                    
                    ScrollView:
                        pos_hint: {'top': 0.9, 'center_x': 0.5}
                        size_hint: 1, 0.9
                        
                        MDBoxLayout:
                            id: drivers_container
                            orientation: 'vertical'
                            spacing: dp(15)
                            padding: dp(15)
                            size_hint_y: None
                            height: self.minimum_height
                            adaptive_height: True
            
            MDTab:
                text: "المغاسل"
                
                MDFloatLayout:
                    
                    MDRaisedButton:
                        text: "إضافة مغسلة"
                        pos_hint: {'top': 0.95, 'right': 0.95}
                        size_hint: None, None
                        size: dp(150), dp(40)
                        on_release: root.add_washing_station()
                    
                    ScrollView:
                        pos_hint: {'top': 0.9, 'center_x': 0.5}
                        size_hint: 1, 0.9
                        
                        MDBoxLayout:
                            id: washing_stations_container
                            orientation: 'vertical'
                            spacing: dp(15)
                            padding: dp(15)
                            size_hint_y: None
                            height: self.minimum_height
                            adaptive_height: True
            
            MDTab:
                text: "الإعلانات"
                
                MDFloatLayout:
                    
                    MDRaisedButton:
                        text: "إعلان جديد"
                        pos_hint: {'top': 0.95, 'right': 0.95}
                        size_hint: None, None
                        size: dp(150), dp(40)
                        on_release: root.add_advertisement()
                    
                    ScrollView:
                        pos_hint: {'top': 0.9, 'center_x': 0.5}
                        size_hint: 1, 0.9
                        
                        MDBoxLayout:
                            id: advertisements_container
                            orientation: 'vertical'
                            spacing: dp(15)
                            padding: dp(15)
                            size_hint_y: None
                            height: self.minimum_height
                            adaptive_height: True
            
            MDTab:
                text: "الباقات"
                
                MDFloatLayout:
                    
                    MDRaisedButton:
                        text: "باقة جديدة"
                        pos_hint: {'top': 0.95, 'right': 0.95}
                        size_hint: None, None
                        size: dp(150), dp(40)
                        on_release: root.add_package()
                    
                    ScrollView:
                        pos_hint: {'top': 0.9, 'center_x': 0.5}
                        size_hint: 1, 0.9
                        
                        MDBoxLayout:
                            id: packages_container
                            orientation: 'vertical'
                            spacing: dp(15)
                            padding: dp(15)
                            size_hint_y: None
                            height: self.minimum_height
                            adaptive_height: True

<AdminUserCard@MDCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(120)
    padding: dp(15)
    spacing: dp(5)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        
        MDLabel:
            id: user_name
            text: ''
            font_style: 'Body1'
            size_hint_x: 0.6
        
        MDLabel:
            id: user_type
            text: ''
            font_style: 'Caption'
            theme_text_color: 'Secondary'
            size_hint_x: 0.4
    
    MDLabel:
        id: user_email
        text: ''
        font_style: 'Body2'
        theme_text_color: 'Secondary'
        size_hint_y: None
        height: dp(25)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        
        MDRaisedButton:
            text: "تعديل"
            size_hint_x: 0.5
            on_release: root.edit_user()
        
        MDFlatButton:
            text: "حذف"
            size_hint_x: 0.5
            on_release: root.delete_user()

<AdminMarketCard@MDCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(100)
    padding: dp(15)
    spacing: dp(5)
    
    MDLabel:
        id: market_name
        text: ''
        font_style: 'Body1'
        size_hint_y: None
        height: dp(30)
    
    MDLabel:
        id: market_location
        text: ''
        font_style: 'Body2'
        theme_text_color: 'Secondary'
        size_hint_y: None
        height: dp(30)
    
    MDRaisedButton:
        text: "إدارة"
        size_hint_y: None
        height: dp(30)
        on_release: root.manage_market()

<AdminDriverCard@MDCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(120)
    padding: dp(15)
    spacing: dp(5)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        
        MDLabel:
            id: driver_name
            text: ''
            font_style: 'Body1'
            size_hint_x: 0.6
        
        MDLabel:
            id: driver_status
            text: ''
            font_style: 'Caption'
            theme_text_color: 'Secondary'
            size_hint_x: 0.4
    
    MDLabel:
        id: driver_vehicle
        text: ''
        font_style: 'Body2'
        theme_text_color: 'Secondary'
        size_hint_y: None
        height: dp(25)
    
    MDLabel:
        id: driver_rating
        text: ''
        font_style: 'Body2'
        theme_text_color: 'Secondary'
        size_hint_y: None
        height: dp(25)
    
    MDRaisedButton:
        text: "تحديث"
        size_hint_y: None
        height: dp(30)
        on_release: root.update_driver()

<AdminWashingStationCard@MDCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(100)
    padding: dp(15)
    spacing: dp(5)
    
    MDLabel:
        id: station_name
        text: ''
        font_style: 'Body1'
        size_hint_y: None
        height: dp(30)
    
    MDLabel:
        id: station_location
        text: ''
        font_style: 'Body2'
        theme_text_color: 'Secondary'
        size_hint_y: None
        height: dp(30)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        
        MDLabel:
            text: "سعر الغسيل:"
            font_style: 'Caption'
            theme_text_color: 'Secondary'
        
        MDLabel:
            id: washing_price
            text: ''
            font_style: 'Caption'
            theme_text_color: 'Primary'

<AdminAdvertisementCard@MDCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(120)
    padding: dp(15)
    spacing: dp(5)
    
    MDLabel:
        id: ad_title
        text: ''
        font_style: 'Body1'
        size_hint_y: None
        height: dp(30)
    
    MDLabel:
        id: ad_content
        text: ''
        font_style: 'Body2'
        theme_text_color: 'Secondary'
        size_hint_y: None
        height: dp(40)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        
        MDLabel:
            id: ad_type
            text: ''
            font_style: 'Caption'
            theme_text_color: 'Secondary'
            size_hint_x: 0.5
        
        MDLabel:
            id: ad_status
            text: ''
            font_style: 'Caption'
            theme_text_color: 'Secondary'
            size_hint_x: 0.5

<AdminPackageCard@MDCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(120)
    padding: dp(15)
    spacing: dp(5)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        
        MDLabel:
            id: package_name
            text: ''
            font_style: 'Body1'
            size_hint_x: 0.6
        
        MDLabel:
            id: package_price
            text: ''
            font_style: 'Body1'
            theme_text_color: 'Primary'
            size_hint_x: 0.4
    
    MDLabel:
        id: package_description
        text: ''
        font_style: 'Body2'
        theme_text_color: 'Secondary'
        size_hint_y: None
        height: dp(40)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(30)
        
        MDLabel:
            id: package_duration
            text: ''
            font_style: 'Caption'
            theme_text_color: 'Secondary'
            size_hint_x: 0.5
        
        MDRaisedButton:
            text: "تفاصيل"
            size_hint_x: 0.5
            on_release: root.show_details()
''')

# تعريف الشاشات
class SplashScreen(Screen):
    pass

class LoginScreen(Screen):
    def login(self):
        email = self.ids.email_input.text
        password = self.ids.password_input.text
        
        if not email or not password:
            MDApp.get_running_app().show_error("يرجى إدخال البريد الإلكتروني وكلمة المرور")
            return
        
        app = MDApp.get_running_app()
        app.login(email, password)
    
    def go_to_register(self):
        self.manager.current = 'register'

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_ui)
    
    def init_ui(self, dt):
        self.ids.buyer_check.bind(active=self.on_user_type_change)
        self.ids.seller_check.bind(active=self.on_user_type_change)
        self.ids.driver_check.bind(active=self.on_user_type_change)
    
    def on_user_type_change(self, checkbox, value):
        if value:
            if checkbox == self.ids.seller_check:
                self.ids.store_name_input.opacity = 1
                self.ids.store_name_input.disabled = False
                self.ids.vehicle_input.opacity = 0
                self.ids.vehicle_input.disabled = True
            elif checkbox == self.ids.driver_check:
                self.ids.store_name_input.opacity = 0
                self.ids.store_name_input.disabled = True
                self.ids.vehicle_input.opacity = 1
                self.ids.vehicle_input.disabled = False
            else:
                self.ids.store_name_input.opacity = 0
                self.ids.store_name_input.disabled = True
                self.ids.vehicle_input.opacity = 0
                self.ids.vehicle_input.disabled = True
    
    def register(self):
        # جمع بيانات التسجيل
        user_data = {
            'name': self.ids.name_input.text,
            'email': self.ids.email_input.text,
            'phone': self.ids.phone_input.text,
            'password': self.ids.password_input.text
        }
        
        # التحقق من كلمة المرور
        if self.ids.password_input.text != self.ids.confirm_password_input.text:
            MDApp.get_running_app().show_error("كلمات المرور غير متطابقة")
            return
        
        # تحديد نوع المستخدم
        if self.ids.seller_check.active:
            user_data['user_type'] = 'seller'
            user_data['store_name'] = self.ids.store_name_input.text
        elif self.ids.driver_check.active:
            user_data['user_type'] = 'driver'
            user_data['vehicle_type'] = self.ids.vehicle_input.text
        else:
            user_data['user_type'] = 'buyer'
        
        # التحقق من الحقول المطلوبة
        if not all([user_data['name'], user_data['email'], user_data['phone'], user_data['password']]):
            MDApp.get_running_app().show_error("جميع الحقول مطلوبة")
            return
        
        app = MDApp.get_running_app()
        app.register(user_data)
    
    def go_to_login(self):
        self.manager.current = 'login'

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loaded = False
    
    def on_enter(self):
        if not self.loaded:
            self.load_home_data()
            self.loaded = True
    
    def load_home_data(self):
        # تحديث الإحصائيات
        app = MDApp.get_running_app()
        self.ids.cart_count_label.text = str(len(app.cart))
        
        # تحميل الأسواق
        self.load_markets()
        
        # تحميل الإعلانات
        self.load_advertisements()
    
    def load_markets(self):
        # بيانات وهمية للأسواق
        markets = [
            {'name': 'سوق صنعاء المركزي', 'location': 'صنعاء', 'products': 120},
            {'name': 'سوق تعز', 'location': 'تعز', 'products': 85},
            {'name': 'سوق الحديدة', 'location': 'الحديدة', 'products': 65},
            {'name': 'سوق إب', 'location': 'إب', 'products': 45}
        ]
        
        container = self.ids.markets_container
        container.clear_widgets()
        
        for market in markets:
            card = MDCard(
                orientation='vertical',
                size_hint=(None, None),
                size=(dp(150), dp(120)),
                padding=dp(10),
                spacing=dp(5)
            )
            
            card.add_widget(MDLabel(
                text=market['name'],
                font_style='Body2',
                halign='center',
                size_hint_y=None,
                height=dp(40)
            ))
            
            card.add_widget(MDLabel(
                text=market['location'],
                font_style='Caption',
                theme_text_color='Secondary',
                halign='center',
                size_hint_y=None,
                height=dp(30)
            ))
            
            card.add_widget(MDLabel(
                text=f"{market['products']} منتج",
                font_style='Caption',
                theme_text_color='Primary',
                halign='center',
                size_hint_y=None,
                height=dp(30)
            ))
            
            container.add_widget(card)
    
    def load_advertisements(self):
        # بيانات وهمية للإعلانات
        ads = [
            {'title': 'خصم 20%', 'desc': 'على جميع أنواع القات'},
            {'title': 'توصيل مجاني', 'desc': 'للطلبات فوق 100 ريال'},
            {'title': 'عروض خاصة', 'desc': 'لفترة محدودة'}
        ]
        
        carousel = self.ids.ads_carousel
        carousel.clear_widgets()
        
        for ad in ads:
            layout = MDFloatLayout(size_hint=(1, 1))
            
            card = MDCard(
                orientation='vertical',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                padding=dp(20),
                spacing=dp(10)
            )
            
            card.add_widget(MDLabel(
                text=ad['title'],
                font_style='H5',
                halign='center',
                theme_text_color='Primary'
            ))
            
            card.add_widget(MDLabel(
                text=ad['desc'],
                font_style='Body1',
                halign='center',
                theme_text_color='Secondary'
            ))
            
            layout.add_widget(card)
            carousel.add_widget(layout)
    
    def nav_to(self, screen):
        app = MDApp.get_running_app()
        if screen in ['orders', 'wallet', 'profile', 'seller_dashboard', 'admin_dashboard'] and not app.user:
            app.show_error("يرجى تسجيل الدخول أولاً")
            self.manager.current = 'login'
            return
        
        # التحقق من الصلاحيات
        if screen == 'seller_dashboard' and app.user['user_type'] != 'seller':
            app.show_error("هذه الصفحة للبائعين فقط")
            return
        
        if screen == 'admin_dashboard' and app.user['user_type'] != 'admin':
            app.show_error("هذه الصفحة للمدير فقط")
            return
        
        self.manager.current = screen
    
    def logout(self):
        app = MDApp.get_running_app()
        app.logout()
    
    def show_notifications(self):
        app = MDApp.get_running_app()
        app.show_notification("إشعارات", f"لديك {len(app.notifications)} إشعار جديد")

class ProductsScreen(Screen):
    def on_enter(self):
        self.load_products()
    
    def load_products(self):
        # تحميل المنتجات من API
        app = MDApp.get_running_app()
        
        def on_success(result):
            if result.get('status') == 'success':
                self.display_products(result['products'])
        
        app.api_request('/api/products', 'GET', callback=on_success)
    
    def display_products(self, products):
        container = self.ids.products_container
        container.clear_widgets()
        
        for product in products[:20]:  # عرض أول 20 منتج فقط
            card = Builder.template('ProductCard')
            card.product_data = product
            card.ids.product_name.text = product['name']
            card.ids.product_price.text = f"{product['price']} ريال"
            
            # تعيين صورة المنتج (إذا وجدت)
            if product.get('images') and len(product['images']) > 0:
                card.ids.product_image.source = product['images'][0]
            else:
                card.ids.product_image.source = 'assets/default_product.png'
            
            container.add_widget(card)
    
    def add_to_cart(self, product):
        app = MDApp.get_running_app()
        
        # عرض خيارات الإضافة
        dialog = MDDialog(
            title="إضافة إلى السلة",
            text=f"هل تريد إضافة {product['name']} إلى السلة؟",
            buttons=[
                MDFlatButton(text="إلغاء", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="إضافة", on_release=lambda x: self.confirm_add(product, dialog))
            ]
        )
        dialog.open()
    
    def confirm_add(self, product, dialog):
        app = MDApp.get_running_app()
        app.add_to_cart(product)
        dialog.dismiss()
    
    def show_filters(self):
        # عرض قائمة الفلاتر
        menu_items = [
            {"text": "الكل", "viewclass": "OneLineListItem", "on_release": lambda x="all": self.filter_products(x)},
            {"text": "قات ممتاز", "viewclass": "OneLineListItem", "on_release": lambda x="premium": self.filter_products(x)},
            {"text": "قات عادي", "viewclass": "OneLineListItem", "on_release": lambda x="regular": self.filter_products(x)},
            {"text": "الأقل سعراً", "viewclass": "OneLineListItem", "on_release": lambda x="price_low": self.filter_products(x)},
            {"text": "الأعلى تقييماً", "viewclass": "OneLineListItem", "on_release": lambda x="rating_high": self.filter_products(x)}
        ]
        
        menu = MDDropdownMenu(
            caller=self.ids.search_input,
            items=menu_items,
            width_mult=4
        )
        menu.open()
    
    def filter_products(self, filter_type):
        print(f"تصفية حسب: {filter_type}")
        # في التطبيق الحقيقي، سيتم إرسال طلب إلى API مع معاملات التصفية
    
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        print(f"تبديل إلى تبويب: {tab_text}")
        # تحميل المنتجات حسب التصنيف
    
    def go_back(self):
        self.manager.current = 'home'
    
    def go_to_cart(self):
        app = MDApp.get_running_app()
        if not app.user:
            app.show_error("يرجى تسجيل الدخول أولاً")
            self.manager.current = 'login'
        else:
            self.manager.current = 'cart'

class CartScreen(Screen):
    def on_enter(self):
        self.update_cart()
    
    def update_cart(self):
        app = MDApp.get_running_app()
        
        container = self.ids.cart_container
        container.clear_widgets()
        
        if not app.cart:
            self.ids.empty_label.opacity = 1
            self.ids.cart_scroll.opacity = 0
            self.ids.checkout_btn.disabled = True
            self.ids.total_label.text = "المجموع: 0 ريال"
            return
        
        self.ids.empty_label.opacity = 0
        self.ids.cart_scroll.opacity = 1
        self.ids.checkout_btn.disabled = False
        
        total = 0
        
        for item in app.cart:
            card = Builder.template('CartItemCard')
            card.item_data = item
            
            product = item['product']
            quantity = item['quantity']
            washing = item.get('washing', False)
            
            card.ids.item_name.text = product['name']
            card.ids.item_price.text = f"{product['price']} ريال"
            card.ids.item_quantity.text = str(quantity)
            card.ids.washing_check.active = washing
            
            item_total = product['price'] * quantity
            if washing:
                item_total += 100
            
            card.ids.item_total.text = f"{item_total} ريال"
            
            total += item_total
            
            container.add_widget(card)
        
        self.ids.total_label.text = f"المجموع: {total} ريال"
    
    def checkout(self):
        app = MDApp.get_running_app()
        if not app.user:
            app.show_error("يرجى تسجيل الدخول أولاً")
            self.manager.current = 'login'
            return
        
        # عرض نموذج إتمام الطلب
        dialog_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(10),
            size_hint_y=None,
            height=dp(300)
        )
        
        dialog_content.add_widget(MDLabel(
            text="إتمام عملية الشراء",
            font_style='H6',
            halign='center'
        ))
        
        address_input = MDTextField(
            hint_text="عنوان التوصيل",
            mode="rectangle",
            size_hint_y=None,
            height=dp(60)
        )
        dialog_content.add_widget(address_input)
        
        dialog_content.add_widget(MDLabel(
            text="طريقة الدفع:",
            font_style='Body1'
        ))
        
        payment_method = "balance"  # Default
        
        def set_payment(method):
            nonlocal payment_method
            payment_method = method
        
        payment_layout = MDBoxLayout(orientation='horizontal', spacing=dp(10))
        
        balance_btn = MDRaisedButton(
            text="رصيد الحساب",
            size_hint_x=0.5,
            on_release=lambda x: set_payment("balance")
        )
        
        wallet_btn = MDFlatButton(
            text="محفظة إلكترونية",
            size_hint_x=0.5,
            on_release=lambda x: set_payment("electronic")
        )
        
        payment_layout.add_widget(balance_btn)
        payment_layout.add_widget(wallet_btn)
        dialog_content.add_widget(payment_layout)
        
        dialog = MDDialog(
            title="تأكيد الطلب",
            type="custom",
            content_cls=dialog_content,
            buttons=[
                MDFlatButton(text="إلغاء", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="تأكيد الطلب", on_release=lambda x: self.confirm_checkout(address_input.text, payment_method, dialog))
            ]
        )
        dialog.open()
    
    def confirm_checkout(self, address, payment_method, dialog):
        if not address.strip():
            MDApp.get_running_app().show_error("يرجى إدخال عنوان التوصيل")
            return
        
        app = MDApp.get_running_app()
        app.create_order(address, payment_method)
        dialog.dismiss()
    
    def go_back(self):
        self.manager.current = 'products'

class OrdersScreen(Screen):
    def on_enter(self):
        self.load_orders()
    
    def load_orders(self):
        app = MDApp.get_running_app()
        
        # تحميل الطلبات من API
        def on_success(result):
            if result.get('status') == 'success':
                self.display_orders(result.get('orders', []))
        
        app.api_request('/api/orders', 'GET', callback=on_success)
    
    def display_orders(self, orders):
        active_container = self.ids.active_orders_container
        past_container = self.ids.past_orders_container
        
        active_container.clear_widgets()
        past_container.clear_widgets()
        
        for order in orders:
            card = Builder.template('OrderCard')
            card.order_data = order
            
            card.ids.order_code.text = f"طلب #{order.get('order_code', '')}"
            card.ids.order_status.text = order.get('status', 'معلق')
            
            # تحديث لون حالة الطلب
            status = order.get('status', '')
            if status == 'مكتمل':
                card.ids.order_status.text_color = (0, 0.5, 0, 1)
            elif status == 'ملغى':
                card.ids.order_status.text_color = (0.9, 0.2, 0.2, 1)
            else:
                card.ids.order_status.text_color = (1, 0.6, 0, 1)
            
            # عرض العناصر
            items_text = ""
            for item in order.get('items', [])[:2]:  # عرض أول عنصرين فقط
                items_text += f"{item.get('product_name', '')} × {item.get('quantity', 1)}\n"
            
            if len(order.get('items', [])) > 2:
                items_text += f"و {len(order.get('items', [])) - 2} عناصر أخرى"
            
            card.ids.order_items.text = items_text.strip()
            card.ids.order_total.text = f"{order.get('total', 0)} ريال"
            card.ids.order_date.text = order.get('created_at', '')[:10]
            
            # تصنيف الطلبات
            if order.get('status') in ['مكتمل', 'ملغى']:
                past_container.add_widget(card)
            else:
                active_container.add_widget(card)
    
    def go_back(self):
        self.manager.current = 'home'
    
    def new_order(self):
        self.manager.current = 'products'

class WalletScreen(Screen):
    def on_enter(self):
        self.load_wallet()
    
    def load_wallet(self):
        app = MDApp.get_running_app()
        
        # تحميل بيانات المحفظة من API
        def on_success(result):
            if result.get('status') == 'success':
                balance = result.get('balance', 0)
                self.ids.balance_label.text = f"{balance} ريال"
                
                # عرض المحافظ الإلكترونية
                self.display_wallets(result.get('wallets', []))
                
                # عرض العمليات الأخيرة
                self.display_transactions(result.get('transactions', []))
        
        # في التطبيق الحقيقي، سيتم استدعاء API مناسب
        # محاكاة البيانات
        wallets = [
            {'name': 'محفظة جيب', 'balance': 150, 'phone': '771234567'},
            {'name': 'محفظة جوالي', 'balance': 0, 'phone': '771234568'},
            {'name': 'محفظة كريمي', 'balance': 300, 'phone': '771234569'}
        ]
        
        transactions = [
            {'description': 'شحن رصيد', 'amount': 100, 'date': '2024-01-15', 'type': 'deposit'},
            {'description': 'شراء منتجات', 'amount': -45, 'date': '2024-01-14', 'type': 'purchase'},
            {'description': 'سحب رصيد', 'amount': -50, 'date': '2024-01-13', 'type': 'withdrawal'},
            {'description': 'شحن رصيد', 'amount': 200, 'date': '2024-01-12', 'type': 'deposit'}
        ]
        
        self.ids.balance_label.text = "350 ريال"
        self.display_wallets(wallets)
        self.display_transactions(transactions)
    
    def display_wallets(self, wallets):
        container = self.ids.wallets_container
        container.clear_widgets()
        
        for wallet in wallets:
            card = Builder.template('WalletCard')
            card.wallet_data = wallet
            
            card.ids.wallet_name.text = wallet['name']
            card.ids.wallet_balance.text = f"{wallet['balance']} ريال"
            
            container.add_widget(card)
    
    def display_transactions(self, transactions):
        container = self.ids.transactions_container
        container.clear_widgets()
        
        for trans in transactions:
            card = Builder.template('TransactionCard')
            
            card.ids.trans_desc.text = trans['description']
            card.ids.trans_date.text = trans['date']
            
            amount = trans['amount']
            if amount > 0:
                card.ids.trans_amount.text = f"+{amount} ريال"
                card.ids.trans_amount.text_color = (0, 0.5, 0, 1)
            else:
                card.ids.trans_amount.text = f"{amount} ريال"
                card.ids.trans_amount.text_color = (0.9, 0.2, 0.2, 1)
            
            container.add_widget(card)
    
    def show_topup_dialog(self):
        dialog_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(10),
            size_hint_y=None,
            height=dp(250)
        )
        
        dialog_content.add_widget(MDLabel(
            text="شحن الرصيد",
            font_style='H6',
            halign='center'
        ))
        
        amount_input = MDTextField(
            hint_text="المبلغ بالريال",
            mode="rectangle",
            input_filter='float',
            size_hint_y=None,
            height=dp(60)
        )
        dialog_content.add_widget(amount_input)
        
        dialog_content.add_widget(MDLabel(
            text="طريقة الشحن:",
            font_style='Body1'
        ))
        
        method_spinner = MDTextField(
            hint_text="اختر طريقة الدفع",
            mode="rectangle",
            size_hint_y=None,
            height=dp(60)
        )
        dialog_content.add_widget(method_spinner)
        
        reference_input = MDTextField(
            hint_text="رقم المرجع أو الإيداع",
            mode="rectangle",
            size_hint_y=None,
            height=dp(60)
        )
        dialog_content.add_widget(reference_input)
        
        dialog = MDDialog(
            title="شحن الرصيد",
            type="custom",
            content_cls=dialog_content,
            buttons=[
                MDFlatButton(text="إلغاء", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="شحن", on_release=lambda x: self.process_topup(amount_input.text, method_spinner.text, reference_input.text, dialog))
            ]
        )
        dialog.open()
    
    def process_topup(self, amount, method, reference, dialog):
        if not amount or not method:
            MDApp.get_running_app().show_error("يرجى إدخال المبلغ وطريقة الدفع")
            return
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                MDApp.get_running_app().show_error("المبلغ يجب أن يكون أكبر من الصفر")
                return
        except:
            MDApp.get_running_app().show_error("المبلغ غير صحيح")
            return
        
        app = MDApp.get_running_app()
        app.topup_wallet(amount, method, reference)
        dialog.dismiss()
    
    def show_withdraw_dialog(self):
        dialog_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(10),
            size_hint_y=None,
            height=dp(300)
        )
        
        dialog_content.add_widget(MDLabel(
            text="سحب الرصيد",
            font_style='H6',
            halign='center'
        ))
        
        amount_input = MDTextField(
            hint_text="المبلغ بالريال",
            mode="rectangle",
            input_filter='float',
            size_hint_y=None,
            height=dp(60)
        )
        dialog_content.add_widget(amount_input)
        
        dialog_content.add_widget(MDLabel(
            text="بيانات المحفظة:",
            font_style='Body1'
        ))
        
        wallet_type = MDTextField(
            hint_text="نوع المحفظة",
            mode="rectangle",
            size_hint_y=None,
            height=dp(60)
        )
        dialog_content.add_widget(wallet_type)
        
        wallet_name = MDTextField(
            hint_text="الاسم الكامل",
            mode="rectangle",
            size_hint_y=None,
            height=dp(60)
        )
        dialog_content.add_widget(wallet_name)
        
        wallet_phone = MDTextField(
            hint_text="رقم الهاتف",
            mode="rectangle",
            size_hint_y=None,
            height=dp(60)
        )
        dialog_content.add_widget(wallet_phone)
        
        dialog = MDDialog(
            title="سحب الرصيد",
            type="custom",
            content_cls=dialog_content,
            buttons=[
                MDFlatButton(text="إلغاء", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="سحب", on_release=lambda x: self.process_withdrawal(amount_input.text, {
                    'wallet_type': wallet_type.text,
                    'name': wallet_name.text,
                    'phone': wallet_phone.text
                }, dialog))
            ]
        )
        dialog.open()
    
    def process_withdrawal(self, amount, wallet_info, dialog):
        if not amount or not wallet_info['wallet_type'] or not wallet_info['phone']:
            MDApp.get_running_app().show_error("جميع الحقول مطلوبة")
            return
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                MDApp.get_running_app().show_error("المبلغ يجب أن يكون أكبر من الصفر")
                return
        except:
            MDApp.get_running_app().show_error("المبلغ غير صحيح")
            return
        
        app = MDApp.get_running_app()
        
        # في التطبيق الحقيقي، سيتم استدعاء API السحب
        app.show_notification("نجاح", "تم تقديم طلب السحب بنجاح، سيتم المعالجة خلال 24 ساعة")
        dialog.dismiss()
    
    def go_back(self):
        self.manager.current = 'home'

class ProfileScreen(Screen):
    def on_enter(self):
        self.load_profile()
    
    def load_profile(self):
        app = MDApp.get_running_app()
        
        if not app.user:
            return
        
        user = app.user
        
        self.ids.profile_name.text = user.get('name', '')
        self.ids.profile_email.text = user.get('email', '')
        self.ids.profile_phone.text = user.get('phone', '')
        self.ids.profile_type.text = user.get('user_type', '')
        
        # بيانات وهمية للإحصائيات
        self.ids.orders_count.text = "12"
        self.ids.total_spent.text = "450 ريال"
        self.ids.user_rating.text = "4.5"
        self.ids.join_date.text = user.get('created_at', '')[:10] if user.get('created_at') else '2024-01-01'
    
    def edit_profile(self):
        app = MDApp.get_running_app()
        app.show_notification("قريباً", "ميزة تعديل الملف الشخصي قريباً")
    
    def logout(self):
        app = MDApp.get_running_app()
        app.logout()
    
    def go_back(self):
        self.manager.current = 'home'

class SellerDashboardScreen(Screen):
    def on_enter(self):
        self.load_seller_data()
    
    def load_seller_data(self):
        # تحميل بيانات البائع
        app = MDApp.get_running_app()
        
        # بيانات وهمية
        self.ids.total_sales.text = "1,250 ريال"
        self.ids.products_count.text = "8"
        self.ids.seller_orders_count.text = "15"
        self.ids.seller_rating.text = "4.7"
        self.ids.seller_balance.text = "350 ريال"
        
        # تحميل منتجات البائع
        self.load_seller_products()
        
        # تحميل طلبات البائع
        self.load_seller_orders()
    
    def load_seller_products(self):
        container = self.ids.seller_products_container
        container.clear_widgets()
        
        # بيانات وهمية
        products = [
            {'name': 'قات صعدي ممتاز', 'price': 60, 'stock': 15},
            {'name': 'قات همداني فاخر', 'price': 55, 'stock': 8},
            {'name': 'قات أرحبي طازج', 'price': 45, 'stock': 20}
        ]
        
        for product in products:
            card = MDCard(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(100),
                padding=dp(15),
                spacing=dp(10)
            )
            
            info_layout = MDBoxLayout(orientation='vertical', spacing=dp(5))
            info_layout.add_widget(MDLabel(
                text=product['name'],
                font_style='Body1'
            ))
            info_layout.add_widget(MDLabel(
                text=f"{product['price']} ريال | متوفر: {product['stock']}",
                font_style='Body2',
                theme_text_color='Secondary'
            ))
            
            card.add_widget(info_layout)
            
            actions = MDBoxLayout(orientation='vertical', size_hint_x=0.3, spacing=dp(5))
            actions.add_widget(MDRaisedButton(
                text="تعديل",
                size_hint_y=None,
                height=dp(30)
            ))
            actions.add_widget(MDFlatButton(
                text="حذف",
                size_hint_y=None,
                height=dp(30)
            ))
            
            card.add_widget(actions)
            container.add_widget(card)
    
    def load_seller_orders(self):
        container = self.ids.seller_orders_container
        container.clear_widgets()
        
        # بيانات وهمية
        orders = [
            {'code': 'ORD001', 'total': 120, 'status': 'قيد التجهيز', 'date': '2024-01-15'},
            {'code': 'ORD002', 'total': 85, 'status': 'تم الشحن', 'date': '2024-01-14'},
            {'code': 'ORD003', 'total': 45, 'status': 'مكتمل', 'date': '2024-01-13'}
        ]
        
        for order in orders:
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(120),
                padding=dp(15),
                spacing=dp(5)
            )
            
            card.add_widget(MDLabel(
                text=f"طلب #{order['code']}",
                font_style='Body1'
            ))
            
            card.add_widget(MDLabel(
                text=f"المجموع: {order['total']} ريال",
                font_style='Body2',
                theme_text_color='Secondary'
            ))
            
            status_layout = MDBoxLayout(orientation='horizontal', spacing=dp(10))
            status_layout.add_widget(MDLabel(
                text=f"الحالة: {order['status']}",
                font_style='Body2'
            ))
            status_layout.add_widget(MDLabel(
                text=order['date'],
                font_style='Caption',
                theme_text_color='Secondary'
            ))
            
            card.add_widget(status_layout)
            container.add_widget(card)
    
    def add_product(self):
        app = MDApp.get_running_app()
        app.show_notification("قريباً", "ميزة إضافة منتج جديد قريباً")
    
    def go_back(self):
        self.manager.current = 'home'

class AdminDashboardScreen(Screen):
    def on_enter(self):
        self.load_admin_data()
    
    def load_admin_data(self):
        # تحميل بيانات لوحة التحكم
        self.load_users()
        self.load_markets()
        self.load_drivers()
        self.load_washing_stations()
        self.load_advertisements()
        self.load_packages()
    
    def load_users(self):
        container = self.ids.users_container
        container.clear_widgets()
        
        # بيانات وهمية
        users = [
            {'name': 'محمد أحمد', 'email': 'mohamed@example.com', 'type': 'مشتري'},
            {'name': 'أحمد علي', 'email': 'ahmed@example.com', 'type': 'بائع'},
            {'name': 'خالد حسن', 'email': 'khaled@example.com', 'type': 'مندوب'}
        ]
        
        for user in users:
            card = Builder.template('AdminUserCard')
            card.user_data = user
            
            card.ids.user_name.text = user['name']
            card.ids.user_email.text = user['email']
            card.ids.user_type.text = user['type']
            
            container.add_widget(card)
    
    def load_markets(self):
        container = self.ids.markets_admin_container
        container.clear_widgets()
        
        # بيانات وهمية
        markets = [
            {'name': 'سوق صنعاء المركزي', 'location': 'صنعاء'},
            {'name': 'سوق تعز', 'location': 'تعز'},
            {'name': 'سوق الحديدة', 'location': 'الحديدة'}
        ]
        
        for market in markets:
            card = Builder.template('AdminMarketCard')
            card.market_data = market
            
            card.ids.market_name.text = market['name']
            card.ids.market_location.text = market['location']
            
            container.add_widget(card)
    
    def load_drivers(self):
        container = self.ids.drivers_container
        container.clear_widgets()
        
        # بيانات وهمية
        drivers = [
            {'name': 'أحمد محمد', 'vehicle': 'دراجة نارية', 'status': 'متاح', 'rating': 4.5},
            {'name': 'محمد علي', 'vehicle': 'سيارة', 'status': 'مشغول', 'rating': 4.2},
            {'name': 'خالد حسن', 'vehicle': 'دراجة نارية', 'status': 'متاح', 'rating': 4.8}
        ]
        
        for driver in drivers:
            card = Builder.template('AdminDriverCard')
            card.driver_data = driver
            
            card.ids.driver_name.text = driver['name']
            card.ids.driver_vehicle.text = driver['vehicle']
            card.ids.driver_status.text = driver['status']
            card.ids.driver_rating.text = f"التقييم: {driver['rating']}"
            
            container.add_widget(card)
    
    def load_washing_stations(self):
        container = self.ids.washing_stations_container
        container.clear_widgets()
        
        # بيانات وهمية
        stations = [
            {'name': 'مغسلة القات المركزية', 'location': 'سوق صنعاء', 'price': 100},
            {'name': 'مغسلة تعز', 'location': 'سوق تعز', 'price': 80},
            {'name': 'مغسلة الحديدة', 'location': 'سوق الحديدة', 'price': 90}
        ]
        
        for station in stations:
            card = Builder.template('AdminWashingStationCard')
            card.station_data = station
            
            card.ids.station_name.text = station['name']
            card.ids.station_location.text = station['location']
            card.ids.washing_price.text = f"{station['price']} ريال"
            
            container.add_widget(card)
    
    def load_advertisements(self):
        container = self.ids.advertisements_container
        container.clear_widgets()
        
        # بيانات وهمية
        ads = [
            {'title': 'خصم 20% على القات', 'content': 'عرض لفترة محدودة', 'type': 'بانر', 'status': 'نشط'},
            {'title': 'توصيل مجاني', 'content': 'للطلبات فوق 100 ريال', 'type': 'نافذة منبثقة', 'status': 'نشط'},
            {'title': 'عروض العيد', 'content': 'عروض خاصة بمناسبة العيد', 'type': 'بانر', 'status': 'منتهي'}
        ]
        
        for ad in ads:
            card = Builder.template('AdminAdvertisementCard')
            card.ad_data = ad
            
            card.ids.ad_title.text = ad['title']
            card.ids.ad_content.text = ad['content']
            card.ids.ad_type.text = ad['type']
            card.ids.ad_status.text = ad['status']
            
            container.add_widget(card)
    
    def load_packages(self):
        container = self.ids.packages_container
        container.clear_widgets()
        
        # بيانات وهمية
        packages = [
            {'name': 'الباقة الأساسية', 'price': 100, 'duration': 30, 'description': 'إعلان لمدة 30 يوم'},
            {'name': 'الباقة المميزة', 'price': 200, 'duration': 60, 'description': 'إعلان مميز لمدة 60 يوم'},
            {'name': 'الباقة الذهبية', 'price': 500, 'duration': 90, 'description': 'إعلان في الصفحة الرئيسية'}
        ]
        
        for package in packages:
            card = Builder.template('AdminPackageCard')
            card.package_data = package
            
            card.ids.package_name.text = package['name']
            card.ids.package_price.text = f"{package['price']} ريال"
            card.ids.package_description.text = package['description']
            card.ids.package_duration.text = f"{package['duration']} يوم"
            
            container.add_widget(card)
    
    def add_user(self):
        MDApp.get_running_app().show_notification("قريباً", "ميزة إضافة مستخدم جديد قريباً")
    
    def add_market(self):
        MDApp.get_running_app().show_notification("قريباً", "ميزة إضافة سوق جديد قريباً")
    
    def add_driver(self):
        MDApp.get_running_app().show_notification("قريباً", "ميزة إضافة مندوب جديد قريباً")
    
    def add_washing_station(self):
        MDApp.get_running_app().show_notification("قريباً", "ميزة إضافة مغسلة جديدة قريباً")
    
    def add_advertisement(self):
        MDApp.get_running_app().show_notification("قريباً", "ميزة إضافة إعلان جديد قريباً")
    
    def add_package(self):
        MDApp.get_running_app().show_notification("قريباً", "ميزة إضافة باقة جديدة قريباً")
    
    def go_back(self):
        self.manager.current = 'home'

if __name__ == '__main__':
    QatApp().run()
