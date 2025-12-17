# -*- coding: utf-8 -*-
"""
شاشة سلة المشتريات ونافذة الشراء
"""
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.menu import MDDropdownMenu

from app.utils.arabic_support import ArabicSupport
from app.utils.api import API
from app.utils.payment import PaymentManager

Builder.load_string('''
<CartItemCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(120)
    padding: dp(10)
    spacing: dp(10)
    elevation: 1
    radius: dp(10)
    
    # صورة المنتج
    MDCard:
        size_hint_x: None
        width: dp(100)
        radius: dp(5)
        elevation: 0
    
    # معلومات المنتج
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(5)
        
        MDLabel:
            text: root.product_name
            font_style: 'Subtitle1'
            theme_text_color: 'Primary'
            font_name: 'DroidArabic'
            bold: True
            size_hint_y: None
            height: dp(30)
            halign: 'right'
        
        MDLabel:
            text: root.product_description
            font_style: 'Body2'
            theme_text_color: 'Secondary'
            font_name: 'DroidArabic'
            size_hint_y: None
            height: dp(25)
            halign: 'right'
        
        MDBoxLayout:
            orientation: 'horizontal'
            adaptive_height: True
            spacing: dp(10)
            
            MDLabel:
                text: f"السعر: {root.product_price} ريال"
                font_style: 'Body2'
                theme_text_color: 'Secondary'
                font_name: 'DroidArabic'
                size_hint_x: 0.6
            
            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(5)
                size_hint_x: 0.4
                adaptive_width: True
                
                MDIconButton:
                    icon: "minus"
                    size_hint: None, None
                    size: dp(30), dp(30)
                    on_press: root.decrease_quantity()
                
                MDLabel:
                    text: str(root.quantity)
                    font_style: 'Body1'
                    theme_text_color: 'Primary'
                    font_name: 'DroidArabic'
                    halign: 'center'
                    size_hint_x: None
                    width: dp(30)
                
                MDIconButton:
                    icon: "plus"
                    size_hint: None, None
                    size: dp(30), dp(30)
                    on_press: root.increase_quantity()
        
        MDLabel:
            text: f"المجموع: {root.item_total} ريال"
            font_style: 'Subtitle2'
            theme_text_color: 'Primary'
            font_name: 'DroidArabic'
            bold: True
            size_hint_y: None
            height: dp(25)
            halign: 'right'
    
    # زر الحذف
    MDIconButton:
        icon: "delete"
        theme_icon_color: "Error"
        on_press: root.remove_item()

<CartScreen>:
    MDScreen:
        md_bg_color: [0.95, 0.95, 0.95, 1]
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            
            # شريط العنوان
            MDCard:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(80)
                padding: dp(10)
                spacing: dp(10)
                elevation: 2
                radius: [0, 0, dp(15), dp(15)]
                
                MDIconButton:
                    icon: "arrow-right"
                    on_press: root.go_back()
                
                MDLabel:
                    text: "سلة المشتريات"
                    font_style: 'H5'
                    theme_text_color: 'Primary'
                    font_name: 'DroidArabic'
                    bold: True
                    size_hint_x: 1
                    halign: 'center'
                
                MDIconButton:
                    icon: "delete-sweep"
                    theme_icon_color: "Error"
                    on_press: root.clear_cart()
            
            # محتوى السلة
            MDBoxLayout:
                orientation: 'vertical'
                id: cart_content
                
                # سيتم تعبئته ديناميكياً

<BuyDialog>:
    orientation: 'vertical'
    spacing: dp(15)
    padding: dp(20)
    size_hint_y: None
    height: dp(600)
    
    MDLabel:
        text: root.product_name
        font_style: 'H5'
        theme_text_color: 'Primary'
        font_name: 'DroidArabic'
        bold: True
        halign: 'center'
        size_hint_y: None
        height: dp(50)
    
    MDLabel:
        text: root.product_description
        font_style: 'Body1'
        theme_text_color: 'Secondary'
        font_name: 'DroidArabic'
        halign: 'center'
        size_hint_y: None
        height: dp(60)
    
    MDLabel:
        text: f"السعر: {root.product_price} ريال"
        font_style: 'H6'
        theme_text_color: 'Primary'
        font_name: 'DroidArabic'
        bold: True
        halign: 'center'
        size_hint_y: None
        height: dp(40)
    
    # الكمية
    MDLabel:
        text: "الكمية:"
        font_style: 'Subtitle1'
        theme_text_color: 'Primary'
        font_name: 'DroidArabic'
        size_hint_y: None
        height: dp(30)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(20)
        size_hint_y: None
        height: dp(50)
        halign: 'center'
        pos_hint: {'center_x': 0.5}
        
        MDIconButton:
            icon: "minus"
            size_hint: None, None
            size: dp(40), dp(40)
            on_press: root.decrease_quantity()
        
        MDLabel:
            id: quantity_label
            text: str(root.quantity)
            font_style: 'H4'
            theme_text_color: 'Primary'
            font_name: 'DroidArabic'
            halign: 'center'
            size_hint_x: 0.3
        
        MDIconButton:
            icon: "plus"
            size_hint: None, None
            size: dp(40), dp(40)
            on_press: root.increase_quantity()
    
    # غسل القات
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(50)
        
        MDCheckbox:
            id: washing_check
            size_hint_x: None
            width: dp(40)
            active: False
        
        MDLabel:
            text: "غسل القات (+100 ريال)"
            font_style: 'Subtitle1'
            theme_text_color: 'Primary'
            font_name: 'DroidArabic'
            size_hint_x: 1
    
    # العنوان
    MDLabel:
        text: "عنوان التوصيل:"
        font_style: 'Subtitle1'
        theme_text_color: 'Primary'
        font_name: 'DroidArabic'
        size_hint_y: None
        height: dp(30)
    
    MDTextField:
        id: address_input
        hint_text: "أدخل عنوان التوصيل الكامل"
        mode: "rectangle"
        multiline: True
        font_name: 'DroidArabic'
        text_direction: 'rtl'
        size_hint_y: None
        height: dp(80)
    
    # طريقة الدفع
    MDLabel:
        text: "طريقة الدفع:"
        font_style: 'Subtitle1'
        theme_text_color: 'Primary'
        font_name: 'DroidArabic'
        size_hint_y: None
        height: dp(30)
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(50)
        
        MDTextField:
            id: payment_method
            hint_text: "اختر طريقة الدفع"
            mode: "rectangle"
            font_name: 'DroidArabic'
            text_direction: 'rtl'
            readonly: True
            size_hint_x: 0.8
        
        MDIconButton:
            icon: "chevron-down"
            on_press: root.show_payment_menu()
    
    # المجموع
    MDCard:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(80)
        padding: dp(15)
        elevation: 1
        radius: dp(10)
        md_bg_color: [0.9, 0.95, 0.9, 1]
        
        MDLabel:
            id: total_label
            text: ""
            font_style: 'H5'
            theme_text_color: 'Primary'
            font_name: 'DroidArabic'
            bold: True
            halign: 'center'
    
    # أزرار
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(50)
        
        MDRaisedButton:
            text: "إتمام الشراء"
            font_name: 'DroidArabic'
            md_bg_color: app.theme_cls.primary_color
            size_hint_x: 0.6
            on_press: root.confirm_purchase()
        
        MDFlatButton:
            text: "إلغاء"
            font_name: 'DroidArabic'
            size_hint_x: 0.4
            on_press: root.dismiss()
''')

class CartItemCard(MDCard):
    """بطاقة عنصر في السلة"""
    product = ObjectProperty(None)
    product_name = StringProperty('')
    product_description = StringProperty('')
    product_price = NumericProperty(0)
    quantity = NumericProperty(1)
    item_total = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(product=self.update_product_info)
        self.bind(quantity=self.update_total)
    
    def update_product_info(self, instance, value):
        """تحديث معلومات المنتج"""
        if self.product:
            self.product_name = self.product.get('name', '')
            self.product_description = self.product.get('description', '')
            self.product_price = self.product.get('price', 0)
            self.update_total()
    
    def update_total(self, *args):
        """تحديث المجموع"""
        self.item_total = self.product_price * self.quantity
    
    def increase_quantity(self):
        """زيادة الكمية"""
        self.quantity += 1
    
    def decrease_quantity(self):
        """تقليل الكمية"""
        if self.quantity > 1:
            self.quantity -= 1
    
    def remove_item(self):
        """حذف العنصر"""
        # إرسال إشارة لحذف العنصر
        from kivy.event import EventDispatcher
        self.dispatch('on_remove', self.product)

class BuyDialog(MDBoxLayout):
    """نافذة الشراء"""
    product = ObjectProperty(None)
    product_name = StringProperty('')
    product_description = StringProperty('')
    product_price = NumericProperty(0)
    quantity = NumericProperty(1)
    washing_price = NumericProperty(100)
    total_price = NumericProperty(0)
    dialog = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_menu = None
        self.bind(product=self.update_product_info)
        self.bind(quantity=self.update_total)
        Clock.schedule_once(self.setup_dialog)
    
    def setup_dialog(self, dt):
        """إعداد النافذة"""
        self.update_product_info()
        self.update_total()
        
        # عرض النافذة
        self.dialog = MDDialog(
            title="شراء المنتج",
            type="custom",
            content_cls=self,
            size_hint=(0.9, None),
            height=dp(650)
        )
    
    def open(self):
        """فتح النافذة"""
        if self.dialog:
            self.dialog.open()
    
    def dismiss(self):
        """إغلاق النافذة"""
        if self.dialog:
            self.dialog.dismiss()
    
    def update_product_info(self, *args):
        """تحديث معلومات المنتج"""
        if self.product:
            self.product_name = self.product.get('name', '')
            self.product_description = self.product.get('description', '')[:100] + '...'
            self.product_price = self.product.get('price', 0)
            self.update_total()
    
    def update_total(self, *args):
        """تحديث المجموع الكلي"""
        washing_required = self.ids.washing_check.active if hasattr(self, 'ids') else False
        washing_cost = self.washing_price if washing_required else 0
        self.total_price = (self.product_price * self.quantity) + washing_cost
        
        if hasattr(self, 'ids'):
            self.ids.total_label.text = f"المجموع: {self.total_price} ريال"
            if hasattr(self.ids, 'quantity_label'):
                self.ids.quantity_label.text = str(self.quantity)
    
    def increase_quantity(self):
        """زيادة الكمية"""
        self.quantity += 1
    
    def decrease_quantity(self):
        """تقليل الكمية"""
        if self.quantity > 1:
            self.quantity -= 1
    
    def show_payment_menu(self):
        """عرض قائمة طرق الدفع"""
        payment_methods = [
            {
                "text": "رصيد الحساب",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="رصيد الحساب": self.set_payment_method(x),
            },
            {
                "text": "محفظة جيب",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="محفظة جيب": self.set_payment_method(x),
            },
            {
                "text": "محفظة جوالي",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="محفظة جوالي": self.set_payment_method(x),
            },
            {
                "text": "محفظة موبايل موني",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="محفظة موبايل موني": self.set_payment_method(x),
            },
            {
                "text": "محفظة الشامل موني",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="محفظة الشامل موني": self.set_payment_method(x),
            },
            {
                "text": "محفظة فلوسك",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="محفظة فلوسك": self.set_payment_method(x),
            },
            {
                "text": "الدفع عند الاستلام",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="الدفع عند الاستلام": self.set_payment_method(x),
            },
        ]
        
        self.payment_menu = MDDropdownMenu(
            caller=self.ids.payment_method,
            items=payment_methods,
            width_mult=4,
            max_height=dp(300),
        )
        self.payment_menu.open()
    
    def set_payment_method(self, method):
        """تعيين طريقة الدفع"""
        self.ids.payment_method.text = method
        if self.payment_menu:
            self.payment_menu.dismiss()
    
    def confirm_purchase(self):
        """تأكيد عملية الشراء"""
        # التحقق من البيانات
        if not self.ids.address_input.text.strip():
            self.ids.address_input.error = True
            self.ids.address_input.helper_text = "يرجى إدخال عنوان التوصيل"
            return
        
        if not self.ids.payment_method.text:
            self.show_error("يرجى اختيار طريقة الدفع")
            return
        
        # جمع بيانات الطلب
        order_data = {
            'product_id': self.product.get('id'),
            'quantity': self.quantity,
            'washing_required': self.ids.washing_check.active,
            'delivery_address': self.ids.address_input.text,
            'payment_method': self.map_payment_method(self.ids.payment_method.text)
        }
        
        # إرسال طلب الشراء
        app = MDApp.get_running_app()
        if not app.user_data:
            self.show_error("يرجى تسجيل الدخول أولاً")
            return
        
        def on_success(response):
            self.dismiss()
            if response.get('success'):
                app.show_success("تم إنشاء الطلب بنجاح!")
                # الانتقال لشاشة الطلبات
                screen_manager = app.screen_manager
                screen_manager.current = 'orders'
            else:
                app.show_error(response.get('message', 'فشل إنشاء الطلب'))
        
        def on_error(error):
            self.dismiss()
            app.show_error("خطأ في الاتصال بالسيرفر")
        
        # استخدام API
        from app.utils.api import API
        api = API()
        api.create_order(order_data, app.user_token, on_success, on_error)
    
    def map_payment_method(self, arabic_method):
        """تحويل طريقة الدفع العربية إلى إنجليزي"""
        mapping = {
            'رصيد الحساب': 'wallet',
            'محفظة جيب': 'jib',
            'محفظة جوالي': 'jawaly',
            'محفظة موبايل موني': 'mobail_money',
            'محفظة الشامل موني': 'shamel_money',
            'محفظة فلوسك': 'floosak',
            'الدفع عند الاستلام': 'cash_on_delivery'
        }
        return mapping.get(arabic_method, 'wallet')
    
    def show_error(self, message):
        """إظهار خطأ"""
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

class CartScreen(Screen):
    """شاشة سلة المشتريات"""
    
    cart_items = ListProperty([])
    cart_total = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = API()
        self.payment_manager = PaymentManager()
        Clock.schedule_once(self.load_cart)
    
    def on_enter(self):
        """عند دخول الشاشة"""
        self.load_cart()
    
    def load_cart(self, dt=None):
        """تحميل محتويات السلة"""
        # في هذا الإصدار، السلة مؤقتة في الذاكرة
        # في الإصدار الكامل، سيتم حفظها في قاعدة البيانات
        app = self.manager.app
        if hasattr(app, 'temp_cart'):
            self.cart_items = app.temp_cart
        else:
            self.cart_items = []
        
        self.update_cart_display()
    
    def update_cart_display(self):
        """تحديث عرض السلة"""
        container = self.ids.cart_content
        container.clear_widgets()
        
        if not self.cart_items:
            # سلة فارغة
            empty_box = MDBoxLayout(
                orientation='vertical',
                spacing=dp(20),
                padding=dp(50),
                size_hint_y=None,
                height=dp(300),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            
            empty_box.add_widget(MDIconButton(
                icon="cart-off",
                icon_size=dp(60),
                theme_icon_color="Secondary",
                pos_hint={'center_x': 0.5}
            ))
            
            empty_box.add_widget(MDLabel(
                text="سلة المشتريات فارغة",
                font_style='H5',
                theme_text_color='Secondary',
                halign='center',
                font_name='DroidArabic'
            ))
            
            empty_box.add_widget(MDLabel(
                text="اذهب للمنتجات لإضافة عناصر",
                font_style='Body1',
                theme_text_color='Hint',
                halign='center',
                font_name='DroidArabic'
            ))
            
            empty_box.add_widget(MDRaisedButton(
                text="تصفح المنتجات",
                font_name='DroidArabic',
                pos_hint={'center_x': 0.5},
                size_hint_x=0.6,
                on_press=lambda x: self.manager.current = 'products'
            ))
            
            container.add_widget(empty_box)
            return
        
        # عرض عناصر السلة
        scroll = MDScrollView()
        items_box = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(15),
            size_hint_y=None,
            adaptive_height=True
        )
        items_box.bind(minimum_height=items_box.setter('height'))
        
        self.cart_total = 0
        
        for item in self.cart_items:
            card = CartItemCard(product=item)
            card.bind(on_remove=lambda instance, product: self.remove_from_cart(product))
            items_box.add_widget(card)
            
            # حساب المجموع
            price = item.get('price', 0)
            quantity = 1  # في هذا الإصاف، الكمية دائماً 1
            self.cart_total += price * quantity
        
        # قسم المجموع الكلي
        total_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=dp(15),
            spacing=dp(10),
            elevation=2,
            radius=dp(10),
            md_bg_color=[0.9, 0.95, 0.9, 1]
        )
        
        total_card.add_widget(MDLabel(
            text="تفاصيل الفاتورة",
            font_style='Subtitle1',
            theme_text_color='Primary',
            font_name='DroidArabic',
            bold=True,
            size_hint_y=None,
            height=dp(30)
        ))
        
        # المجموع الفرعي
        subtotal_box = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True
        )
        subtotal_box.add_widget(MDLabel(
            text="المجموع الفرعي:",
            font_style='Body2',
            theme_text_color='Secondary',
            font_name='DroidArabic',
            size_hint_x=0.7
        ))
        subtotal_box.add_widget(MDLabel(
            text=f"{self.cart_total} ريال",
            font_style='Body2',
            theme_text_color='Primary',
            font_name='DroidArabic',
            halign='right',
            size_hint_x=0.3
        ))
        total_card.add_widget(subtotal_box)
        
        # الضريبة (0% في اليمن)
        tax_box = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True
        )
        tax_box.add_widget(MDLabel(
            text="الضريبة:",
            font_style='Body2',
            theme_text_color='Secondary',
            font_name='DroidArabic',
            size_hint_x=0.7
        ))
        tax_box.add_widget(MDLabel(
            text="0 ريال",
            font_style='Body2',
            theme_text_color='Primary',
            font_name='DroidArabic',
            halign='right',
            size_hint_x=0.3
        ))
        total_card.add_widget(tax_box)
        
        # المجموع الكلي
        total_box = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True
        )
        total_box.add_widget(MDLabel(
            text="المجموع الكلي:",
            font_style='Subtitle1',
            theme_text_color='Primary',
            font_name='DroidArabic',
            bold=True,
            size_hint_x=0.7
        ))
        total_box.add_widget(MDLabel(
            text=f"{self.cart_total} ريال",
            font_style='Subtitle1',
            theme_text_color='Primary',
            font_name='DroidArabic',
            bold=True,
            halign='right',
            size_hint_x=0.3
        ))
        total_card.add_widget(total_box)
        
        items_box.add_widget(total_card)
        
        # زر إتمام الشراء
        checkout_btn = MDRaisedButton(
            text="إتمام الشراء",
            font_name='DroidArabic',
            font_size='18sp',
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5},
            on_press=self.checkout
        )
        items_box.add_widget(checkout_btn)
        
        scroll.add_widget(items_box)
        container.add_widget(scroll)
    
    def remove_from_cart(self, product):
        """حذف منتج من السلة"""
        app = self.manager.app
        if hasattr(app, 'temp_cart'):
            app.temp_cart = [item for item in app.temp_cart if item.get('id') != product.get('id')]
            self.cart_items = app.temp_cart
        
        self.update_cart_display()
        self.manager.app.show_success("تم حذف المنتج من السلة")
    
    def clear_cart(self):
        """تفريغ السلة"""
        app = self.manager.app
        if hasattr(app, 'temp_cart') and app.temp_cart:
            app.temp_cart = []
            self.cart_items = []
            self.update_cart_display()
            self.manager.app.show_success("تم تفريغ السلة")
    
    def checkout(self, instance):
        """إتمام عملية الشراء"""
        if not self.cart_items:
            self.show_error("السلة فارغة")
            return
        
        # في هذا الإصدار البسيط، نفتح نافذة شراء لكل منتج
        # في الإصدار الكامل، ستكون هناك عملية شراء جماعية
        product = self.cart_items[0]  # أول منتج في السلة
        buy_dialog = BuyDialog(product=product)
        buy_dialog.open()
    
    def go_back(self):
        """العودة للشاشة السابقة"""
        self.manager.current = 'products'
    
    def show_error(self, message):
        """إظهار خطأ"""
        self.manager.app.show_error(message)
