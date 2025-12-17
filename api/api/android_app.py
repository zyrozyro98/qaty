import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.carousel import Carousel
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.picker import MDDatePicker, MDTimePicker
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.chip import MDChip
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.boxlayout import MDBoxLayout

import requests
import json
from datetime import datetime, timedelta
import threading
from functools import partial
import os
from kivy.storage.jsonstore import JsonStore

# تكوين النافذة
Window.size = (400, 700)
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# عنوان API
API_BASE_URL = "https://qaty.onrender.com/api"

# تخزين محلي
store = JsonStore('qaty_app_data.json')

# شاشة التحميل الأولي
class LoadingScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.check_auth, 2)
    
    def check_auth(self, dt):
        token = store.get('auth')['token'] if 'auth' in store else None
        if token:
            self.manager.current = 'home'
        else:
            self.manager.current = 'login'

# شاشة تسجيل الدخول
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
    
    def login(self):
        email = self.ids.email_input.text
        password = self.ids.password_input.text
        
        if not email or not password:
            self.show_error("يرجى إدخال البريد الإلكتروني وكلمة المرور")
            return
        
        # عرض مؤشر التحميل
        self.show_loading("جاري تسجيل الدخول...")
        
        # إرسال طلب تسجيل الدخول
        threading.Thread(target=self.perform_login, args=(email, password)).start()
    
    def perform_login(self, email, password):
        try:
            response = requests.post(f"{API_BASE_URL}/auth/login", json={
                'email': email,
                'password': password
            })
            
            data = response.json()
            
            Clock.schedule_once(lambda dt: self.handle_login_response(data))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"خطأ في الاتصال: {str(e)}"))
    
    def handle_login_response(self, data):
        self.hide_loading()
        
        if 'error' in data:
            self.show_error(data['error'])
        else:
            # حفظ بيانات المصادقة
            store.put('auth', token=data['access_token'], user=json.dumps(data['user']))
            store.put('user', **data['user'])
            
            self.show_success(f"مرحباً {data['user']['name']}!")
            self.manager.current = 'home'
    
    def go_to_register(self):
        self.manager.current = 'register'
    
    def show_error(self, message):
        Snackbar(
            text=message,
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(Window.width - 20) / Window.width,
            bg_color=(0.9, 0.2, 0.2, 1)
        ).open()
    
    def show_success(self, message):
        Snackbar(
            text=message,
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(Window.width - 20) / Window.width,
            bg_color=(0.2, 0.7, 0.3, 1)
        ).open()
    
    def show_loading(self, message):
        self.dialog = MDDialog(
            title=message,
            type="custom",
            size_hint=(0.8, 0.2)
        )
        self.dialog.open()
    
    def hide_loading(self):
        if self.dialog:
            self.dialog.dismiss()

# شاشة التسجيل
class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
    
    def register(self):
        # جمع البيانات
        user_data = {
            'name': self.ids.name_input.text,
            'email': self.ids.email_input.text,
            'phone': self.ids.phone_input.text,
            'password': self.ids.password_input.text,
            'user_type': self.ids.user_type_input.text
        }
        
        # التحقق من البيانات
        if not all(user_data.values()):
            self.show_error("يرجى ملء جميع الحقول")
            return
        
        if user_data['password'] != self.ids.confirm_password_input.text:
            self.show_error("كلمات المرور غير متطابقة")
            return
        
        # عرض مؤشر التحميل
        self.show_loading("جاري إنشاء الحساب...")
        
        # إرسال طلب التسجيل
        threading.Thread(target=self.perform_register, args=(user_data,)).start()
    
    def perform_register(self, user_data):
        try:
            response = requests.post(f"{API_BASE_URL}/auth/register", json=user_data)
            data = response.json()
            
            Clock.schedule_once(lambda dt: self.handle_register_response(data))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"خطأ في الاتصال: {str(e)}"))
    
    def handle_register_response(self, data):
        self.hide_loading()
        
        if 'error' in data:
            self.show_error(data['error'])
        else:
            # حفظ بيانات المصادقة
            store.put('auth', token=data['access_token'], user=json.dumps(data['user']))
            store.put('user', **data['user'])
            
            self.show_success("تم إنشاء الحساب بنجاح!")
            self.manager.current = 'home'
    
    def go_to_login(self):
        self.manager.current = 'login'
    
    def show_error(self, message):
        Snackbar(text=message, bg_color=(0.9, 0.2, 0.2, 1)).open()
    
    def show_success(self, message):
        Snackbar(text=message, bg_color=(0.2, 0.7, 0.3, 1)).open()
    
    def show_loading(self, message):
        self.dialog = MDDialog(title=message)
        self.dialog.open()
    
    def hide_loading(self):
        if self.dialog:
            self.dialog.dismiss()

# الشاشة الرئيسية
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_type = None
        self.balance = 0
        self.notifications_count = 0
    
    def on_enter(self):
        self.load_user_data()
        self.load_balance()
        self.load_notifications()
        self.load_ads()
    
    def load_user_data(self):
        if 'user' in store:
            user = store.get('user')
            self.user_type = user.get('user_type')
            self.ids.welcome_label.text = f"مرحباً، {user.get('name', 'مستخدم')}"
    
    def load_balance(self):
        token = store.get('auth')['token'] if 'auth' in store else None
        if token:
            try:
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.get(f"{API_BASE_URL}/wallets/balance", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.balance = data.get('balance', 0)
                    self.ids.balance_label.text = f"رصيدك: {self.balance} ريال"
            except:
                pass
    
    def load_notifications(self):
        token = store.get('auth')['token'] if 'auth' in store else None
        if token:
            try:
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.get(f"{API_BASE_URL}/notifications/unread", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.notifications_count = data.get('count', 0)
                    self.ids.notifications_badge.text = str(self.notifications_count)
            except:
                pass
    
    def load_ads(self):
        try:
            response = requests.get(f"{API_BASE_URL}/admin/advertisements")
            if response.status_code == 200:
                data = response.json()
                ads = data.get('advertisements', [])
                if ads:
                    self.ids.ads_carousel.clear_widgets()
                    for ad in ads:
                        if ad.get('is_active'):
                            ad_card = MDCard(
                                size_hint=(0.9, 0.8),
                                padding=10,
                                radius=[15, 15, 15, 15]
                            )
                            ad_card.add_widget(Label(
                                text=ad['title'],
                                font_size='18sp',
                                bold=True,
                                color=(0, 0, 0, 1)
                            ))
                            self.ids.ads_carousel.add_widget(ad_card)
        except:
            pass
    
    def go_to_products(self):
        self.manager.current = 'products'
    
    def go_to_orders(self):
        self.manager.current = 'orders'
    
    def go_to_wallet(self):
        self.manager.current = 'wallet'
    
    def go_to_profile(self):
        self.manager.current = 'profile'
    
    def go_to_sellers(self):
        if self.user_type == 'buyer':
            self.manager.current = 'sellers'
        else:
            self.show_message("هذه الصفحة للمشترين فقط")
    
    def go_to_notifications(self):
        self.manager.current = 'notifications'
    
    def logout(self):
        store.clear()
        self.manager.current = 'login'
    
    def show_message(self, message):
        Snackbar(text=message).open()

# شاشة المنتجات
class ProductsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.products = []
        self.selected_category = None
        self.selected_market = None
    
    def on_enter(self):
        self.load_products()
        self.load_categories()
        self.load_markets()
    
    def load_products(self):
        token = store.get('auth')['token'] if 'auth' in store else None
        if token:
            try:
                headers = {'Authorization': f'Bearer {token}'}
                params = {}
                if self.selected_category:
                    params['category'] = self.selected_category
                if self.selected_market:
                    params['market_id'] = self.selected_market
                
                response = requests.get(f"{API_BASE_URL}/products", 
                                      headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    self.products = data.get('products', [])
                    self.display_products()
            except Exception as e:
                self.show_error(f"خطأ في تحميل المنتجات: {str(e)}")
    
    def load_categories(self):
        # قائمة الفئات الثابتة
        categories = ['صعدي', 'همداني', 'أرحبي', 'حيوفي', 'نقفة', 'روس']
        self.ids.categories_layout.clear_widgets()
        
        # إضافة زر "الكل"
        all_chip = MDChip(
            text="الكل",
            on_press=lambda x: self.filter_by_category(None)
        )
        self.ids.categories_layout.add_widget(all_chip)
        
        for category in categories:
            chip = MDChip(
                text=category,
                on_press=lambda x, cat=category: self.filter_by_category(cat)
            )
            self.ids.categories_layout.add_widget(chip)
    
    def load_markets(self):
        try:
            response = requests.get(f"{API_BASE_URL}/admin/markets")
            if response.status_code == 200:
                data = response.json()
                markets = data.get('markets', [])
                
                menu_items = [{
                    "text": "جميع الأسواق",
                    "on_release": lambda m=None: self.filter_by_market(None)
                }]
                
                for market in markets:
                    if market.get('is_active'):
                        menu_items.append({
                            "text": market['name'],
                            "on_release": lambda m=market['id']: self.filter_by_market(m)
                        })
                
                self.market_menu = MDDropdownMenu(
                    caller=self.ids.market_filter_btn,
                    items=menu_items,
                    width_mult=4
                )
        except:
            pass
    
    def display_products(self):
        self.ids.products_grid.clear_widgets()
        
        if not self.products:
            self.ids.products_grid.add_widget(Label(
                text="لا توجد منتجات متاحة",
                font_size='18sp',
                color=(0.5, 0.5, 0.5, 1),
                halign='center'
            ))
            return
        
        for product in self.products:
            card = self.create_product_card(product)
            self.ids.products_grid.add_widget(card)
    
    def create_product_card(self, product):
        card = MDCard(
            orientation='vertical',
            size_hint=(None, None),
            size=('180dp', '250dp'),
            padding='10dp',
            spacing='10dp',
            radius=[15, 15, 15, 15]
        )
        
        # صورة المنتج
        image = Image(
            source='assets/product_placeholder.png' if not product.get('image_url') else product['image_url'],
            size_hint=(1, 0.5),
            allow_stretch=True
        )
        card.add_widget(image)
        
        # معلومات المنتج
        info_layout = BoxLayout(orientation='vertical', spacing='5dp')
        
        name_label = Label(
            text=product['name'],
            font_size='14sp',
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height='30dp',
            halign='right'
        )
        info_layout.add_widget(name_label)
        
        price_label = Label(
            text=f"{product['price']} ريال",
            font_size='16sp',
            bold=True,
            color=(0.2, 0.7, 0.3, 1),
            size_hint_y=None,
            height='25dp'
        )
        info_layout.add_widget(price_label)
        
        seller_label = Label(
            text=f"البائع: {product.get('seller_name', 'غير معروف')}",
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height='20dp'
        )
        info_layout.add_widget(seller_label)
        
        card.add_widget(info_layout)
        
        # زر الإضافة للسلة
        buy_btn = MDRaisedButton(
            text="أضف للسلة",
            size_hint=(1, None),
            height='40dp',
            on_press=lambda x, p=product: self.add_to_cart(p)
        )
        card.add_widget(buy_btn)
        
        return card
    
    def add_to_cart(self, product):
        # التحقق من تسجيل الدخول
        if 'auth' not in store:
            self.show_error("يرجى تسجيل الدخول أولاً")
            self.manager.current = 'login'
            return
        
        # عرض نافذة اختيار الكمية
        self.show_quantity_dialog(product)
    
    def show_quantity_dialog(self, product):
        dialog_content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        dialog_content.add_widget(Label(
            text=f"اختر كمية {product['name']}",
            font_size='18sp',
            bold=True
        ))
        
        quantity_input = TextInput(
            text="1",
            input_type='number',
            size_hint=(1, None),
            height='50dp',
            font_size='20sp',
            halign='center'
        )
        dialog_content.add_widget(quantity_input)
        
        # خيار الغسيل
        washing_check = MDCheckbox(
            size_hint=(None, None),
            size=('30dp', '30dp')
        )
        
        washing_layout = BoxLayout(orientation='horizontal', spacing='10dp')
        washing_layout.add_widget(washing_check)
        washing_layout.add_widget(Label(
            text=f"غسيل القات (+100 ريال)",
            font_size='14sp'
        ))
        dialog_content.add_widget(washing_layout)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing='10dp')
        
        def add_to_cart(dialog_instance):
            try:
                quantity = int(quantity_input.text)
                requires_washing = washing_check.active
                
                if quantity <= 0:
                    self.show_error("الكمية يجب أن تكون أكبر من الصفر")
                    return
                
                # حفظ في السلة المحلية
                cart_item = {
                    'product': product,
                    'quantity': quantity,
                    'requires_washing': requires_washing
                }
                
                cart = store.get('cart')['items'] if 'cart' in store else []
                cart.append(cart_item)
                store.put('cart', items=cart)
                
                dialog_instance.dismiss()
                self.show_success(f"تم إضافة {quantity} من {product['name']} إلى السلة")
                
            except ValueError:
                self.show_error("الكمية غير صالحة")
        
        add_btn = MDRaisedButton(text="إضافة", on_press=add_to_cart)
        cancel_btn = MDFlatButton(text="إلغاء")
        
        buttons_layout.add_widget(add_btn)
        buttons_layout.add_widget(cancel_btn)
        dialog_content.add_widget(buttons_layout)
        
        dialog = MDDialog(
            title="إضافة إلى السلة",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, None)
        )
        
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        dialog.open()
    
    def filter_by_category(self, category):
        self.selected_category = category
        self.load_products()
    
    def filter_by_market(self, market_id):
        self.selected_market = market_id
        self.ids.market_filter_btn.text = "اختر السوق" if not market_id else f"السوق: {market_id}"
        if self.market_menu:
            self.market_menu.dismiss()
        self.load_products()
    
    def go_to_cart(self):
        if 'auth' not in store:
            self.show_error("يرجى تسجيل الدخول أولاً")
            self.manager.current = 'login'
        else:
            self.manager.current = 'cart'
    
    def show_error(self, message):
        Snackbar(text=message, bg_color=(0.9, 0.2, 0.2, 1)).open()
    
    def show_success(self, message):
        Snackbar(text=message, bg_color=(0.2, 0.7, 0.3, 1)).open()

# شاشة السلة
class CartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_items = []
    
    def on_enter(self):
        self.load_cart()
    
    def load_cart(self):
        self.cart_items = store.get('cart')['items'] if 'cart' in store else []
        self.display_cart()
        self.calculate_total()
    
    def display_cart(self):
        self.ids.cart_items_layout.clear_widgets()
        
        if not self.cart_items:
            self.ids.cart_items_layout.add_widget(Label(
                text="السلة فارغة",
                font_size='18sp',
                color=(0.5, 0.5, 0.5, 1),
                halign='center'
            ))
            return
        
        for i, item in enumerate(self.cart_items):
            cart_item_card = self.create_cart_item_card(item, i)
            self.ids.cart_items_layout.add_widget(cart_item_card)
    
    def create_cart_item_card(self, item, index):
        product = item['product']
        quantity = item['quantity']
        
        card = MDCard(
            orientation='horizontal',
            size_hint=(1, None),
            height='100dp',
            padding='10dp',
            spacing='10dp',
            radius=[10, 10, 10, 10]
        )
        
        # معلومات المنتج
        info_layout = BoxLayout(orientation='vertical', spacing='5dp')
        
        info_layout.add_widget(Label(
            text=product['name'],
            font_size='14sp',
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height='25dp',
            halign='right'
        ))
        
        info_layout.add_widget(Label(
            text=f"الكمية: {quantity}",
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height='20dp'
        ))
        
        if item.get('requires_washing'):
            info_layout.add_widget(Label(
                text="✓ مع الغسيل (+100 ريال)",
                font_size='12sp',
                color=(0.2, 0.7, 0.3, 1),
                size_hint_y=None,
                height='20dp'
            ))
        
        card.add_widget(info_layout)
        
        # السعر
        price_layout = BoxLayout(orientation='vertical', size_hint_x=0.3)
        
        item_price = product['price'] * quantity
        if item.get('requires_washing'):
            item_price += 100
        
        price_layout.add_widget(Label(
            text=f"{item_price} ريال",
            font_size='16sp',
            bold=True,
            color=(0.2, 0.7, 0.3, 1)
        ))
        
        card.add_widget(price_layout)
        
        # زر الحذف
        delete_btn = MDIconButton(
            icon="delete",
            theme_text_color="Custom",
            text_color=(0.9, 0.2, 0.2, 1),
            on_press=lambda x, idx=index: self.remove_item(idx)
        )
        card.add_widget(delete_btn)
        
        return card
    
    def remove_item(self, index):
        self.cart_items.pop(index)
        store.put('cart', items=self.cart_items)
        self.load_cart()
    
    def calculate_total(self):
        total = 0
        for item in self.cart_items:
            item_total = item['product']['price'] * item['quantity']
            if item.get('requires_washing'):
                item_total += 100
            total += item_total
        
        self.ids.total_label.text = f"المجموع: {total} ريال"
        self.total_amount = total
    
    def checkout(self):
        if not self.cart_items:
            self.show_error("السلة فارغة")
            return
        
        # عرض نافذة تأكيد الشراء
        self.show_checkout_dialog()
    
    def show_checkout_dialog(self):
        dialog_content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        dialog_content.add_widget(Label(
            text="تأكيد الشراء",
            font_size='20sp',
            bold=True
        ))
        
        # عنوان التوصيل
        dialog_content.add_widget(Label(
            text="عنوان التوصيل:",
            font_size='14sp'
        ))
        
        address_input = TextInput(
            multiline=True,
            size_hint=(1, None),
            height='80dp',
            hint_text="أدخل عنوان التوصيل الكامل"
        )
        dialog_content.add_widget(address_input)
        
        # ملاحظات
        dialog_content.add_widget(Label(
            text="ملاحظات:",
            font_size='14sp'
        ))
        
        notes_input = TextInput(
            multiline=True,
            size_hint=(1, None),
            height='60dp',
            hint_text="ملاحظات إضافية (اختياري)"
        )
        dialog_content.add_widget(notes_input)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing='10dp')
        
        def confirm_checkout(dialog_instance):
            if not address_input.text.strip():
                self.show_error("يرجى إدخال عنوان التوصيل")
                return
            
            dialog_instance.dismiss()
            self.process_checkout(address_input.text, notes_input.text)
        
        confirm_btn = MDRaisedButton(text="تأكيد الشراء", on_press=confirm_checkout)
        cancel_btn = MDFlatButton(text="إلغاء")
        
        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)
        dialog_content.add_widget(buttons_layout)
        
        dialog = MDDialog(
            title="إتمام الطلب",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.7)
        )
        
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        dialog.open()
    
    def process_checkout(self, address, notes):
        # إنشاء طلب لكل عنصر في السلة
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            self.show_error("يرجى تسجيل الدخول أولاً")
            self.manager.current = 'login'
            return
        
        headers = {'Authorization': f'Bearer {token}'}
        
        successful_orders = []
        
        for item in self.cart_items:
            try:
                order_data = {
                    'product_id': item['product']['id'],
                    'quantity': item['quantity'],
                    'requires_washing': item.get('requires_washing', False),
                    'delivery_address': address,
                    'notes': notes
                }
                
                response = requests.post(f"{API_BASE_URL}/orders/create", 
                                       json=order_data, headers=headers)
                
                if response.status_code == 201:
                    order = response.json().get('order')
                    successful_orders.append(order)
                    
                    # تأكيد الدفع
                    confirm_response = requests.post(
                        f"{API_BASE_URL}/orders/confirm/{order['id']}",
                        headers=headers
                    )
                    
            except Exception as e:
                self.show_error(f"خطأ في إنشاء الطلب: {str(e)}")
        
        if successful_orders:
            # تفريغ السلة
            store.put('cart', items=[])
            
            # عرض نجاح العملية
            self.show_success(f"تم إنشاء {len(successful_orders)} طلب بنجاح")
            self.manager.current = 'orders'
        else:
            self.show_error("فشل في إنشاء الطلبات")
    
    def show_error(self, message):
        Snackbar(text=message, bg_color=(0.9, 0.2, 0.2, 1)).open()
    
    def show_success(self, message):
        Snackbar(text=message, bg_color=(0.2, 0.7, 0.3, 1)).open()

# شاشة الطلبات
class OrdersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orders = []
        self.user_type = None
    
    def on_enter(self):
        self.load_user_type()
        self.load_orders()
    
    def load_user_type(self):
        if 'user' in store:
            user = store.get('user')
            self.user_type = user.get('user_type')
    
    def load_orders(self):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            self.show_error("يرجى تسجيل الدخول أولاً")
            self.manager.current = 'login'
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{API_BASE_URL}/orders/my-orders", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.orders = data.get('orders', [])
                self.display_orders()
            else:
                self.show_error("فشل في تحميل الطلبات")
                
        except Exception as e:
            self.show_error(f"خطأ في الاتصال: {str(e)}")
    
    def display_orders(self):
        self.ids.orders_list.clear_widgets()
        
        if not self.orders:
            self.ids.orders_list.add_widget(Label(
                text="لا توجد طلبات",
                font_size='18sp',
                color=(0.5, 0.5, 0.5, 1),
                halign='center'
            ))
            return
        
        for order in self.orders:
            order_item = self.create_order_item(order)
            self.ids.orders_list.add_widget(order_item)
    
    def create_order_item(self, order):
        item = ThreeLineListItem(
            text=f"طلب #{order.get('order_code', order['id'])}",
            secondary_text=f"الحالة: {order['status']} | المبلغ: {order['total_price']} ريال",
            tertiary_text=f"التاريخ: {order['created_at'][:10]}",
            on_press=lambda x, o=order: self.show_order_details(o)
        )
        
        # تلوين الحالة
        status_color = self.get_status_color(order['status'])
        item.secondary_text_color = status_color
        
        return item
    
    def get_status_color(self, status):
        status_colors = {
            'pending': (1, 0.6, 0, 1),      # برتقالي
            'confirmed': (0.2, 0.7, 0.3, 1),  # أخضر
            'washing': (0.3, 0.5, 0.8, 1),    # أزرق
            'delivering': (0.7, 0.3, 0.7, 1), # بنفسجي
            'delivered': (0.2, 0.7, 0.3, 1),  # أخضر
            'cancelled': (0.9, 0.2, 0.2, 1)   # أحمر
        }
        return status_colors.get(status, (0.5, 0.5, 0.5, 1))
    
    def show_order_details(self, order):
        dialog_content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        details = [
            f"رقم الطلب: {order.get('order_code', order['id'])}",
            f"الحالة: {order['status']}",
            f"المبلغ: {order['total_price']} ريال",
            f"الكمية: {order['quantity']}",
            f"سعر الوحدة: {order['unit_price']} ريال",
        ]
        
        if order.get('washing_price', 0) > 0:
            details.append(f"سعر الغسيل: {order['washing_price']} ريال")
        
        if order.get('sale_code'):
            details.append(f"رمز البيع: {order['sale_code']}")
        
        if order.get('delivery_address'):
            details.append(f"عنوان التوصيل: {order['delivery_address']}")
        
        if order.get('driver_name'):
            details.append(f"المندوب: {order['driver_name']}")
        
        if order.get('estimated_delivery'):
            details.append(f"التوصيل المتوقع: {order['estimated_delivery']}")
        
        for detail in details:
            dialog_content.add_widget(Label(
                text=detail,
                font_size='14sp',
                size_hint_y=None,
                height='30dp'
            ))
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing='10dp')
        
        # إضافة أزرار إضافية حسب الحالة ونوع المستخدم
        if self.user_type == 'driver' and order['status'] == 'delivering':
            deliver_btn = MDRaisedButton(
                text="تسليم الطلب",
                on_press=lambda x: self.deliver_order(order['id'])
            )
            buttons_layout.add_widget(deliver_btn)
        
        close_btn = MDFlatButton(text="إغلاق")
        buttons_layout.add_widget(close_btn)
        
        dialog_content.add_widget(buttons_layout)
        
        dialog = MDDialog(
            title="تفاصيل الطلب",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.8)
        )
        
        close_btn.bind(on_press=lambda x: dialog.dismiss())
        dialog.open()
    
    def deliver_order(self, order_id):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.post(f"{API_BASE_URL}/orders/{order_id}/deliver", headers=headers)
            
            if response.status_code == 200:
                self.show_success("تم تسليم الطلب بنجاح")
                self.load_orders()
            else:
                self.show_error("فشل في تسليم الطلب")
                
        except Exception as e:
            self.show_error(f"خطأ في الاتصال: {str(e)}")
    
    def refresh_orders(self):
        self.load_orders()
        self.show_success("تم تحديث الطلبات")
    
    def show_error(self, message):
        Snackbar(text=message, bg_color=(0.9, 0.2, 0.2, 1)).open()
    
    def show_success(self, message):
        Snackbar(text=message, bg_color=(0.2, 0.7, 0.3, 1)).open()

# شاشة المحفظة
class WalletScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.balance = 0
        self.transactions = []
    
    def on_enter(self):
        self.load_balance()
        self.load_transactions()
    
    def load_balance(self):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            self.show_error("يرجى تسجيل الدخول أولاً")
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{API_BASE_URL}/wallets/balance", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.balance = data.get('balance', 0)
                self.ids.balance_label.text = f"{self.balance} ريال"
            else:
                self.show_error("فشل في تحميل الرصيد")
                
        except Exception as e:
            self.show_error(f"خطأ في الاتصال: {str(e)}")
    
    def load_transactions(self):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{API_BASE_URL}/wallets/transactions", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.transactions = data.get('transactions', [])
                self.display_transactions()
                
        except Exception as e:
            self.show_error(f"خطأ في تحميل المعاملات: {str(e)}")
    
    def display_transactions(self):
        self.ids.transactions_list.clear_widgets()
        
        if not self.transactions:
            self.ids.transactions_list.add_widget(Label(
                text="لا توجد معاملات",
                font_size='14sp',
                color=(0.5, 0.5, 0.5, 1),
                halign='center'
            ))
            return
        
        for transaction in self.transactions:
            transaction_item = self.create_transaction_item(transaction)
            self.ids.transactions_list.add_widget(transaction_item)
    
    def create_transaction_item(self, transaction):
        amount = transaction['amount']
        transaction_type = transaction['transaction_type']
        
        # تحديد النص واللون
        if amount > 0:
            amount_text = f"+{amount} ريال"
            color = (0.2, 0.7, 0.3, 1)  # أخضر
        else:
            amount_text = f"{amount} ريال"
            color = (0.9, 0.2, 0.2, 1)  # أحمر
        
        type_text = self.get_transaction_type_text(transaction_type)
        
        item = TwoLineListItem(
            text=f"{type_text}: {amount_text}",
            secondary_text=f"{transaction.get('notes', '')} | {transaction['created_at'][:10]}",
            on_press=lambda x, t=transaction: self.show_transaction_details(t)
        )
        
        item.text_color = color
        
        return item
    
    def get_transaction_type_text(self, transaction_type):
        types = {
            'deposit': 'إيداع',
            'withdrawal': 'سحب',
            'purchase': 'شراء',
            'sale': 'بيع',
            'refund': 'استرداد',
            'gift': 'هدية'
        }
        return types.get(transaction_type, transaction_type)
    
    def show_transaction_details(self, transaction):
        dialog_content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        details = [
            f"النوع: {self.get_transaction_type_text(transaction['transaction_type'])}",
            f"المبلغ: {transaction['amount']} ريال",
            f"الحالة: {transaction['status']}",
            f"الرقم المرجعي: {transaction['reference_number']}",
            f"التاريخ: {transaction['created_at']}",
        ]
        
        if transaction.get('payment_method'):
            details.append(f"طريقة الدفع: {transaction['payment_method']}")
        
        if transaction.get('notes'):
            details.append(f"ملاحظات: {transaction['notes']}")
        
        for detail in details:
            dialog_content.add_widget(Label(
                text=detail,
                font_size='14sp',
                size_hint_y=None,
                height='30dp'
            ))
        
        close_btn = MDFlatButton(text="إغلاق")
        dialog_content.add_widget(close_btn)
        
        dialog = MDDialog(
            title="تفاصيل المعاملة",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.7)
        )
        
        close_btn.bind(on_press=lambda x: dialog.dismiss())
        dialog.open()
    
    def show_deposit_options(self):
        menu_items = [
            {
                "text": "محفظة جيب",
                "on_release": lambda: self.show_deposit_dialog("محفظة جيب")
            },
            {
                "text": "محفظة جوالي",
                "on_release": lambda: self.show_deposit_dialog("محفظة جوالي")
            },
            {
                "text": "محفظة موبايل موني",
                "on_release": lambda: self.show_deposit_dialog("محفظة موبايل موني")
            },
            {
                "text": "محفظة الشامل موني",
                "on_release": lambda: self.show_deposit_dialog("محفظة الشامل موني")
            },
            {
                "text": "محفظة فلوسك",
                "on_release": lambda: self.show_deposit_dialog("محفظة فلوسك")
            },
            {
                "text": "كود هدية",
                "on_release": self.show_gift_code_dialog
            }
        ]
        
        self.deposit_menu = MDDropdownMenu(
            caller=self.ids.deposit_btn,
            items=menu_items,
            width_mult=4
        )
        self.deposit_menu.open()
    
    def show_deposit_dialog(self, payment_method):
        dialog_content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        dialog_content.add_widget(Label(
            text=f"إيداع عبر {payment_method}",
            font_size='18sp',
            bold=True
        ))
        
        dialog_content.add_widget(Label(
            text="أرسل المبلغ إلى الرقم: 771831482",
            font_size='14sp',
            color=(0.3, 0.3, 0.3, 1)
        ))
        
        dialog_content.add_widget(Label(
            text="اسم المستلم: يوسف محمد علي حمود زهير",
            font_size='14sp',
            color=(0.3, 0.3, 0.3, 1)
        ))
        
        dialog_content.add_widget(Label(
            text="أدخل المبلغ والرقم المرجعي:",
            font_size='14sp'
        ))
        
        amount_input = TextInput(
            hint_text="المبلغ بالريال",
            input_type='number',
            size_hint=(1, None),
            height='50dp'
        )
        dialog_content.add_widget(amount_input)
        
        reference_input = TextInput(
            hint_text="الرقم المرجعي للحوالة",
            size_hint=(1, None),
            height='50dp'
        )
        dialog_content.add_widget(reference_input)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing='10dp')
        
        def submit_deposit(dialog_instance):
            try:
                amount = float(amount_input.text)
                reference = reference_input.text.strip()
                
                if amount <= 0:
                    self.show_error("المبلغ يجب أن يكون أكبر من الصفر")
                    return
                
                if not reference:
                    self.show_error("الرقم المرجعي مطلوب")
                    return
                
                dialog_instance.dismiss()
                self.process_deposit(amount, payment_method, reference)
                
            except ValueError:
                self.show_error("المبلغ غير صالح")
        
        submit_btn = MDRaisedButton(text="تأكيد الإيداع", on_press=submit_deposit)
        cancel_btn = MDFlatButton(text="إلغاء")
        
        buttons_layout.add_widget(submit_btn)
        buttons_layout.add_widget(cancel_btn)
        dialog_content.add_widget(buttons_layout)
        
        dialog = MDDialog(
            title="إيداع أموال",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.8)
        )
        
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        dialog.open()
    
    def show_gift_code_dialog(self):
        dialog_content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        dialog_content.add_widget(Label(
            text="إدخال كود هدية",
            font_size='18sp',
            bold=True
        ))
        
        code_input = TextInput(
            hint_text="أدخل كود الهدية",
            size_hint=(1, None),
            height='50dp'
        )
        dialog_content.add_widget(code_input)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing='10dp')
        
        def validate_gift_code(dialog_instance):
            code = code_input.text.strip()
            
            if not code:
                self.show_error("يرجى إدخال كود الهدية")
                return
            
            dialog_instance.dismiss()
            self.process_gift_code(code)
        
        validate_btn = MDRaisedButton(text="تفعيل الكود", on_press=validate_gift_code)
        cancel_btn = MDFlatButton(text="إلغاء")
        
        buttons_layout.add_widget(validate_btn)
        buttons_layout.add_widget(cancel_btn)
        dialog_content.add_widget(buttons_layout)
        
        dialog = MDDialog(
            title="كود هدية",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.4)
        )
        
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        dialog.open()
    
    def process_deposit(self, amount, payment_method, reference):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            self.show_error("يرجى تسجيل الدخول أولاً")
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            deposit_data = {
                'amount': amount,
                'payment_method': payment_method,
                'reference_number': reference,
                'notes': f'إيداع عبر {payment_method}'
            }
            
            response = requests.post(f"{API_BASE_URL}/wallets/deposit", 
                                   json=deposit_data, headers=headers)
            
            if response.status_code == 200:
                self.show_success("تم تقديم طلب الإيداع بنجاح")
                self.load_balance()
                self.load_transactions()
            else:
                data = response.json()
                self.show_error(data.get('error', 'فشل في الإيداع'))
                
        except Exception as e:
            self.show_error(f"خطأ في الاتصال: {str(e)}")
    
    def process_gift_code(self, code):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            self.show_error("يرجى تسجيل الدخول أولاً")
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            gift_data = {'code': code}
            
            response = requests.post(f"{API_BASE_URL}/wallets/gift-code/validate", 
                                   json=gift_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.show_success(data.get('message', 'تم تفعيل الكود'))
                self.load_balance()
                self.load_transactions()
            else:
                data = response.json()
                self.show_error(data.get('error', 'كود غير صالح'))
                
        except Exception as e:
            self.show_error(f"خطأ في الاتصال: {str(e)}")
    
    def show_withdraw_dialog(self):
        dialog_content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        dialog_content.add_widget(Label(
            text="سحب أموال",
            font_size='18sp',
            bold=True
        ))
        
        # اختيار نوع المحفظة
        wallet_type_input = TextInput(
            hint_text="نوع المحفظة (جيب، جوالي، إلخ)",
            size_hint=(1, None),
            height='50dp'
        )
        dialog_content.add_widget(wallet_type_input)
        
        wallet_number_input = TextInput(
            hint_text="رقم المحفظة",
            size_hint=(1, None),
            height='50dp'
        )
        dialog_content.add_widget(wallet_number_input)
        
        amount_input = TextInput(
            hint_text="المبلغ بالريال",
            input_type='number',
            size_hint=(1, None),
            height='50dp'
        )
        dialog_content.add_widget(amount_input)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing='10dp')
        
        def submit_withdrawal(dialog_instance):
            try:
                wallet_type = wallet_type_input.text.strip()
                wallet_number = wallet_number_input.text.strip()
                amount = float(amount_input.text)
                
                if not wallet_type or not wallet_number:
                    self.show_error("يرجى إدخال بيانات المحفظة")
                    return
                
                if amount <= 0:
                    self.show_error("المبلغ يجب أن يكون أكبر من الصفر")
                    return
                
                if amount > self.balance:
                    self.show_error("رصيد غير كافي")
                    return
                
                dialog_instance.dismiss()
                self.process_withdrawal(amount, wallet_type, wallet_number)
                
            except ValueError:
                self.show_error("المبلغ غير صالح")
        
        submit_btn = MDRaisedButton(text="طلب السحب", on_press=submit_withdrawal)
        cancel_btn = MDFlatButton(text="إلغاء")
        
        buttons_layout.add_widget(submit_btn)
        buttons_layout.add_widget(cancel_btn)
        dialog_content.add_widget(buttons_layout)
        
        dialog = MDDialog(
            title="سحب أموال",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.7)
        )
        
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        dialog.open()
    
    def process_withdrawal(self, amount, wallet_type, wallet_number):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            self.show_error("يرجى تسجيل الدخول أولاً")
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            withdraw_data = {
                'amount': amount,
                'wallet_type': wallet_type,
                'wallet_number': wallet_number
            }
            
            response = requests.post(f"{API_BASE_URL}/wallets/withdraw", 
                                   json=withdraw_data, headers=headers)
            
            if response.status_code == 200:
                self.show_success("تم تقديم طلب السحب بنجاح")
                self.load_balance()
                self.load_transactions()
            else:
                data = response.json()
                self.show_error(data.get('error', 'فشل في السحب'))
                
        except Exception as e:
            self.show_error(f"خطأ في الاتصال: {str(e)}")
    
    def refresh_wallet(self):
        self.load_balance()
        self.load_transactions()
        self.show_success("تم تحديث المحفظة")
    
    def show_error(self, message):
        Snackbar(text=message, bg_color=(0.9, 0.2, 0.2, 1)).open()
    
    def show_success(self, message):
        Snackbar(text=message, bg_color=(0.2, 0.7, 0.3, 1)).open()

# شاشة الملف الشخصي
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = {}
    
    def on_enter(self):
        self.load_user_data()
    
    def load_user_data(self):
        if 'user' in store:
            self.user_data = store.get('user')
            self.display_user_data()
    
    def display_user_data(self):
        self.ids.name_label.text = self.user_data.get('name', 'غير معروف')
        self.ids.email_label.text = self.user_data.get('email', 'غير معروف')
        self.ids.phone_label.text = self.user_data.get('phone', 'غير معروف')
        self.ids.type_label.text = self.user_data.get('user_type', 'مستخدم')
        
        if self.user_data.get('store_name'):
            self.ids.store_label.text = f"اسم المتجر: {self.user_data['store_name']}"
            self.ids.store_label.opacity = 1
        else:
            self.ids.store_label.opacity = 0
        
        if self.user_data.get('vehicle_type'):
            self.ids.vehicle_label.text = f"نوع المركبة: {self.user_data['vehicle_type']}"
            self.ids.vehicle_label.opacity = 1
        else:
            self.ids.vehicle_label.opacity = 0
    
    def edit_profile(self):
        dialog_content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        dialog_content.add_widget(Label(
            text="تعديل الملف الشخصي",
            font_size='18sp',
            bold=True
        ))
        
        name_input = TextInput(
            text=self.user_data.get('name', ''),
            hint_text="الاسم الكامل",
            size_hint=(1, None),
            height='50dp'
        )
        dialog_content.add_widget(name_input)
        
        phone_input = TextInput(
            text=self.user_data.get('phone', ''),
            hint_text="رقم الهاتف",
            size_hint=(1, None),
            height='50dp'
        )
        dialog_content.add_widget(phone_input)
        
        # حقول إضافية حسب نوع المستخدم
        user_type = self.user_data.get('user_type')
        
        if user_type == 'seller':
            store_input = TextInput(
                text=self.user_data.get('store_name', ''),
                hint_text="اسم المتجر",
                size_hint=(1, None),
                height='50dp'
            )
            dialog_content.add_widget(store_input)
        
        elif user_type == 'driver':
            vehicle_input = TextInput(
                text=self.user_data.get('vehicle_type', ''),
                hint_text="نوع المركبة",
                size_hint=(1, None),
                height='50dp'
            )
            dialog_content.add_widget(vehicle_input)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing='10dp')
        
        def save_profile(dialog_instance):
            updated_data = {
                'name': name_input.text.strip(),
                'phone': phone_input.text.strip()
            }
            
            if user_type == 'seller' and 'store_input' in locals():
                updated_data['store_name'] = store_input.text.strip()
            elif user_type == 'driver' and 'vehicle_input' in locals():
                updated_data['vehicle_type'] = vehicle_input.text.strip()
            
            dialog_instance.dismiss()
            self.update_profile(updated_data)
        
        save_btn = MDRaisedButton(text="حفظ", on_press=save_profile)
        cancel_btn = MDFlatButton(text="إلغاء")
        
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        dialog_content.add_widget(buttons_layout)
        
        dialog = MDDialog(
            title="تعديل الملف",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.6)
        )
        
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        dialog.open()
    
    def update_profile(self, updated_data):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            self.show_error("يرجى تسجيل الدخول أولاً")
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.put(f"{API_BASE_URL}/auth/profile/update", 
                                  json=updated_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # تحديث البيانات المحلية
                self.user_data.update(updated_data)
                store.put('user', **self.user_data)
                
                self.display_user_data()
                self.show_success("تم تحديث الملف الشخصي")
            else:
                data = response.json()
                self.show_error(data.get('error', 'فشل في التحديث'))
                
        except Exception as e:
            self.show_error(f"خطأ في الاتصال: {str(e)}")
    
    def setup_wallet(self):
        dialog_content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        dialog_content.add_widget(Label(
            text="إعداد المحفظة الإلكترونية",
            font_size='18sp',
            bold=True
        ))
        
        wallets = [
            ('jib_wallet', 'محفظة جيب'),
            ('jawaly_wallet', 'محفظة جوالي'),
            ('mobile_money_wallet', 'محفظة موبايل موني'),
            ('shamel_money_wallet', 'محفظة الشامل موني'),
            ('fulusik_wallet', 'محفظة فلوسك')
        ]
        
        wallet_inputs = {}
        
        for wallet_key, wallet_name in wallets:
            dialog_content.add_widget(Label(
                text=wallet_name,
                font_size='14sp'
            ))
            
            wallet_input = TextInput(
                hint_text="رقم المحفظة",
                size_hint=(1, None),
                height='50dp'
            )
            wallet_inputs[wallet_key] = wallet_input
            dialog_content.add_widget(wallet_input)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing='10dp')
        
        def save_wallet_info(dialog_instance):
            wallet_data = {}
            for wallet_key, wallet_input in wallet_inputs.items():
                if wallet_input.text.strip():
                    wallet_data[wallet_key] = wallet_input.text.strip()
            
            dialog_instance.dismiss()
            self.save_wallet_setup(wallet_data)
        
        save_btn = MDRaisedButton(text="حفظ", on_press=save_wallet_info)
        cancel_btn = MDFlatButton(text="إلغاء")
        
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        dialog_content.add_widget(buttons_layout)
        
        dialog = MDDialog(
            title="إعداد المحفظة",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.9)
        )
        
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        dialog.open()
    
    def save_wallet_setup(self, wallet_data):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            self.show_error("يرجى تسجيل الدخول أولاً")
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.post(f"{API_BASE_URL}/auth/wallet/setup", 
                                   json=wallet_data, headers=headers)
            
            if response.status_code == 200:
                self.show_success("تم إعداد المحفظة بنجاح")
            else:
                data = response.json()
                self.show_error(data.get('error', 'فشل في الإعداد'))
                
        except Exception as e:
            self.show_error(f"خطأ في الاتصال: {str(e)}")
    
    def logout(self):
        store.clear()
        self.manager.current = 'login'
        self.show_success("تم تسجيل الخروج بنجاح")
    
    def show_error(self, message):
        Snackbar(text=message, bg_color=(0.9, 0.2, 0.2, 1)).open()
    
    def show_success(self, message):
        Snackbar(text=message, bg_color=(0.2, 0.7, 0.3, 1)).open()

# شاشة الإشعارات
class NotificationsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notifications = []
    
    def on_enter(self):
        self.load_notifications()
    
    def load_notifications(self):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{API_BASE_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.notifications = data.get('notifications', [])
                self.display_notifications()
                
        except Exception as e:
            self.show_error(f"خطأ في تحميل الإشعارات: {str(e)}")
    
    def display_notifications(self):
        self.ids.notifications_list.clear_widgets()
        
        if not self.notifications:
            self.ids.notifications_list.add_widget(Label(
                text="لا توجد إشعارات",
                font_size='18sp',
                color=(0.5, 0.5, 0.5, 1),
                halign='center'
            ))
            return
        
        for notification in self.notifications:
            notification_item = self.create_notification_item(notification)
            self.ids.notifications_list.add_widget(notification_item)
    
    def create_notification_item(self, notification):
        item = ThreeLineListItem(
            text=notification['title'],
            secondary_text=notification['message'],
            tertiary_text=notification['created_at'][:16],
            on_press=lambda x, n=notification: self.show_notification_details(n)
        )
        
        # تلوين العناصر غير المقروءة
        if not notification['is_read']:
            item.bg_color = (0.9, 0.95, 1, 1)
        
        return item
    
    def show_notification_details(self, notification):
        dialog_content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        dialog_content.add_widget(Label(
            text=notification['title'],
            font_size='18sp',
            bold=True
        ))
        
        dialog_content.add_widget(Label(
            text=notification['message'],
            font_size='14sp',
            size_hint_y=None,
            height='100dp'
        ))
        
        dialog_content.add_widget(Label(
            text=f"التاريخ: {notification['created_at']}",
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1)
        ))
        
        if notification.get('data'):
            dialog_content.add_widget(Label(
                text="بيانات إضافية:",
                font_size='12sp',
                bold=True
            ))
            
            for key, value in notification['data'].items():
                dialog_content.add_widget(Label(
                    text=f"{key}: {value}",
                    font_size='12sp',
                    size_hint_y=None,
                    height='20dp'
                ))
        
        close_btn = MDFlatButton(text="إغلاق")
        dialog_content.add_widget(close_btn)
        
        dialog = MDDialog(
            title="تفاصيل الإشعار",
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.7)
        )
        
        close_btn.bind(on_press=lambda x: dialog.dismiss())
        dialog.open()
        
        # وضع علامة كمقروء إذا لم تكن مقروءة
        if not notification['is_read']:
            self.mark_as_read([notification['id']])
    
    def mark_as_read(self, notification_ids):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.post(f"{API_BASE_URL}/notifications/mark-read", 
                                   json={'notification_ids': notification_ids}, 
                                   headers=headers)
            
            if response.status_code == 200:
                self.load_notifications()
                
        except Exception as e:
            print(f"Error marking as read: {e}")
    
    def mark_all_read(self):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.post(f"{API_BASE_URL}/notifications/mark-all-read", 
                                   headers=headers)
            
            if response.status_code == 200:
                self.show_success("تم قراءة جميع الإشعارات")
                self.load_notifications()
                
        except Exception as e:
            self.show_error(f"خطأ في تحديث الإشعارات: {str(e)}")
    
    def refresh_notifications(self):
        self.load_notifications()
        self.show_success("تم تحديث الإشعارات")
    
    def show_error(self, message):
        Snackbar(text=message, bg_color=(0.9, 0.2, 0.2, 1)).open()
    
    def show_success(self, message):
        Snackbar(text=message, bg_color=(0.2, 0.7, 0.3, 1)).open()

# شاشة البائعين (للمشترين)
class SellersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sellers = []
    
    def on_enter(self):
        self.load_sellers()
    
    def load_sellers(self):
        token = store.get('auth')['token'] if 'auth' in store else None
        if not token:
            self.show_error("يرجى تسجيل الدخول أولاً")
            return
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{API_BASE_URL}/users", headers=headers, 
                                  params={'user_type': 'seller', 'is_active': 'true'})
            
            if response.status_code == 200:
                data = response.json()
                self.sellers = data.get('users', [])
                self.display_sellers()
            else:
                self.show_error("فشل في تحميل البائعين")
                
        except Exception as e:
            self.show_error(f"خطأ في الاتصال: {str(e)}")
    
    def display_sellers(self):
        self.ids.sellers_grid.clear_widgets()
        
        if not self.sellers:
            self.ids.sellers_grid.add_widget(Label(
                text="لا توجد بائعين",
                font_size='18sp',
                color=(0.5, 0.5, 0.5, 1),
                halign='center'
            ))
            return
        
        for seller in self.sellers:
            seller_card = self.create_seller_card(seller)
            self.ids.sellers_grid.add_widget(seller_card)
    
    def create_seller_card(self, seller):
        card = MDCard(
            orientation='vertical',
            size_hint=(None, None),
            size=('180dp', '200dp'),
            padding='10dp',
            spacing='10dp',
            radius=[15, 15, 15, 15]
        )
        
        # معلومات البائع
        card.add_widget(Label(
            text=seller['name'],
            font_size='16sp',
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height='40dp',
            halign='center'
        ))
        
        if seller.get('store_name'):
            card.add_widget(Label(
                text=seller['store_name'],
                font_size='14sp',
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height='30dp',
                halign='center'
            ))
        
        # التقييم
        rating = seller.get('rating', 0)
        card.add_widget(Label(
            text=f"التقييم: {rating:.1f} ⭐",
            font_size='14sp',
            color=(1, 0.8, 0, 1),
            size_hint_y=None,
            height='30dp',
            halign='center'
        ))
        
        # زر عرض المنتجات
        view_btn = MDRaisedButton(
            text="عرض المنتجات",
            size_hint=(1, None),
            height='40dp',
            on_press=lambda x, s=seller: self.view_seller_products(s)
        )
        card.add_widget(view_btn)
        
        return card
    
    def view_seller_products(self, seller):
        # تمرير معرف البائع إلى شاشة المنتجات
        self.manager.get_screen('products').selected_seller = seller['id']
        self.manager.current = 'products'
    
    def show_error(self, message):
        Snackbar(text=message, bg_color=(0.9, 0.2, 0.2, 1)).open()

# تطبيق Android الرئيسي
class QatyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        self.screen_manager = None
    
    def build(self):
        self.screen_manager = ScreenManager()
        
        # إضافة الشاشات
        self.screen_manager.add_widget(LoadingScreen(name='loading'))
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(RegisterScreen(name='register'))
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(ProductsScreen(name='products'))
        self.screen_manager.add_widget(CartScreen(name='cart'))
        self.screen_manager.add_widget(OrdersScreen(name='orders'))
        self.screen_manager.add_widget(WalletScreen(name='wallet'))
        self.screen_manager.add_widget(ProfileScreen(name='profile'))
        self.screen_manager.add_widget(NotificationsScreen(name='notifications'))
        self.screen_manager.add_widget(SellersScreen(name='sellers'))
        
        return self.screen_manager
    
    def on_start(self):
        # بدء الاتصال بالخادم
        self.check_server_connection()
    
    def check_server_connection(self):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ تم الاتصال بالخادم بنجاح")
            else:
                print("⚠️ الخادم يستجيب ولكن بحالة خطأ")
        except Exception as e:
            print(f"❌ فشل الاتصال بالخادم: {e}")
            # يمكن عرض رسالة للمستخدم هنا

if __name__ == '__main__':
    QatyApp().run()
