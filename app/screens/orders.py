# -*- coding: utf-8 -*-
"""
شاشة الطلبات - عرض وتتبع الطلبات
"""
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.clock import Clock
from kivy.metrics import dp
from datetime import datetime

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.chip import MDChip
from kivymd.uix.menu import MDDropdownMenu

from app.utils.arabic_support import ArabicSupport
from app.utils.api import API

Builder.load_string('''
<OrderCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(220)
    padding: dp(15)
    spacing: dp(10)
    elevation: 2
    radius: dp(15)
    
    # رأس البطاقة
    MDBoxLayout:
        orientation: 'horizontal'
        adaptive_height: True
        
        MDLabel:
            text: f"طلب #{root.order_code}"
            font_style: 'H6'
            theme_text_color: 'Primary'
            font_name: 'DroidArabic'
            bold: True
            size_hint_x: 0.7
        
        MDChip:
            id: status_chip
            text: ""
            icon: ""
            size_hint: None, None
            size: dp(100), dp(30)
            line_color: [0, 0, 0, 0]
    
    # معلومات الطلب
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(5)
        adaptive_height: True
        
        MDBoxLayout:
            orientation: 'horizontal'
            adaptive_height: True
            
            MDLabel:
                text: "المنتج:"
                font_style: 'Body2'
                theme_text_color: 'Secondary'
                font_name: 'DroidArabic'
                size_hint_x: 0.3
            
            MDLabel:
                text: root.product_name
                font_style: 'Body2'
                theme_text_color: 'Primary'
                font_name: 'DroidArabic'
                size_hint_x: 0.7
                halign: 'right'
        
        MDBoxLayout:
            orientation: 'horizontal'
            adaptive_height: True
            
            MDLabel:
                text: "الكمية:"
                font_style: 'Body2'
                theme_text_color: 'Secondary'
                font_name: 'DroidArabic'
                size_hint_x: 0.3
            
            MDLabel:
                text: str(root.quantity)
                font_style: 'Body2'
                theme_text_color: 'Primary'
                font_name: 'DroidArabic'
                size_hint_x: 0.7
                halign: 'right'
        
        MDBoxLayout:
            orientation: 'horizontal'
            adaptive_height: True
            
            MDLabel:
                text: "المجموع:"
                font_style: 'Body2'
                theme_text_color: 'Secondary'
                font_name: 'DroidArabic'
                size_hint_x: 0.3
            
            MDLabel:
                text: f"{root.total_price} ريال"
                font_style: 'Body2'
                theme_text_color: 'Primary'
                font_name: 'DroidArabic'
                size_hint_x: 0.7
                halign: 'right'
        
        MDBoxLayout:
            orientation: 'horizontal'
            adaptive_height: True
            
            MDLabel:
                text: "التاريخ:"
                font_style: 'Body2'
                theme_text_color: 'Secondary'
                font_name: 'DroidArabic'
                size_hint_x: 0.3
            
            MDLabel:
                text: root.order_date
                font_style: 'Body2'
                theme_text_color: 'Primary'
                font_name: 'DroidArabic'
                size_hint_x: 0.7
                halign: 'right'
    
    # أزرار الإجراءات
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        adaptive_height: True
        
        MDFlatButton:
            text: "تفاصيل"
            font_name: 'DroidArabic'
            size_hint_x: 0.5
            on_press: root.show_details()
        
        MDRaisedButton:
            id: action_button
            text: ""
            font_name: 'DroidArabic'
            size_hint_x: 0.5
            md_bg_color: app.theme_cls.primary_color

<OrdersScreen>:
    MDScreen:
        md_bg_color: [0.95, 0.95, 0.95, 1]
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            
            # شريط العنوان والتصفية
            MDCard:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(120)
                padding: dp(10)
                spacing: dp(10)
                elevation: 2
                radius: [0, 0, dp(15), dp(15)]
                
                # العنوان
                MDBoxLayout:
                    orientation: 'horizontal'
                    adaptive_height: True
                    
                    MDIconButton:
                        icon: "arrow-right"
                        on_press: root.go_back()
                    
                    MDLabel:
                        text: "طلباتي"
                        font_style: 'H5'
                        theme_text_color: 'Primary'
                        font_name: 'DroidArabic'
                        bold: True
                        size_hint_x: 1
                        halign: 'center'
                    
                    MDIconButton:
                        icon: "plus"
                        on_press: root.create_new_order()
                
                # التصفية حسب الحالة
                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(10)
                    adaptive_height: True
                    
                    MDFlatButton:
                        text: "الكل"
                        font_name: 'DroidArabic'
                        on_press: root.filter_orders("الكل")
                    
                    MDFlatButton:
                        text: "قيد الانتظار"
                        font_name: 'DroidArabic'
                        on_press: root.filter_orders("pending")
                    
                    MDFlatButton:
                        text: "قيد التجهيز"
                        font_name: 'DroidArabic'
                        on_press: root.filter_orders("preparing")
                    
                    MDFlatButton:
                        text: "قيد التوصيل"
                        font_name: 'DroidArabic'
                        on_press: root.filter_orders("delivering")
            
            # قائمة الطلبات
            MDBoxLayout:
                orientation: 'vertical'
                id: orders_container
''')

class OrderCard(MDCard):
    """بطاقة طلب"""
    order = ObjectProperty(None)
    order_id = NumericProperty(0)
    order_code = StringProperty('')
    product_name = StringProperty('')
    quantity = NumericProperty(1)
    total_price = NumericProperty(0)
    order_date = StringProperty('')
    status = StringProperty('pending')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(order=self.update_order_info)
        Clock.schedule_once(self.setup_card)
    
    def setup_card(self, dt):
        """إعداد البطاقة"""
        if self.order:
            self.update_order_info()
    
    def update_order_info(self, *args):
        """تحديث معلومات الطلب"""
        if self.order:
            self.order_id = self.order.get('id', 0)
            self.order_code = self.order.get('order_code', '')
            self.product_name = self.order.get('product_name', '')
            self.quantity = self.order.get('quantity', 1)
            self.total_price = self.order.get('final_price', 0)
            
            # تحويل التاريخ
            created_at = self.order.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    self.order_date = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    self.order_date = created_at
            
            self.status = self.order.get('status', 'pending')
            self.update_status_display()
    
    def update_status_display(self):
        """تحديث عرض الحالة"""
        status_config = {
            'pending': {'text': 'قيد الانتظار', 'color': [0.96, 0.80, 0.18, 1], 'icon': 'clock'},
            'confirmed': {'text': 'تم التأكيد', 'color': [0.30, 0.69, 0.31, 1], 'icon': 'check'},
            'preparing': {'text': 'قيد التجهيز', 'color': [0.25, 0.60, 0.85, 1], 'icon': 'cog'},
            'washing': {'text': 'قيد الغسل', 'color': [0.49, 0.34, 0.76, 1], 'icon': 'water'},
            'delivering': {'text': 'قيد التوصيل', 'color': [0.96, 0.52, 0.09, 1], 'icon': 'truck'},
            'delivered': {'text': 'تم التوصيل', 'color': [0.30, 0.69, 0.31, 1], 'icon': 'check-circle'},
            'cancelled': {'text': 'ملغي', 'color': [0.96, 0.26, 0.21, 1], 'icon': 'close-circle'}
        }
        
        config = status_config.get(self.status, status_config['pending'])
        
        chip = self.ids.status_chip
        chip.text = config['text']
        chip.icon = config['icon']
        chip.md_bg_color = config['color']
        
        # تحديث زر الإجراء
        action_btn = self.ids.action_button
        if self.status == 'pending':
            action_btn.text = "تأكيد"
            action_btn.md_bg_color = [0.30, 0.69, 0.31, 1]
        elif self.status == 'delivered':
            action_btn.text = "تقييم"
            action_btn.md_bg_color = [0.96, 0.80, 0.18, 1]
        elif self.status == 'delivering':
            action_btn.text = "تتبع"
            action_btn.md_bg_color = [0.25, 0.60, 0.85, 1]
        else:
            action_btn.text = "تفاصيل"
            action_btn.md_bg_color = self.theme_cls.primary_color
    
    def show_details(self):
        """عرض تفاصيل الطلب"""
        dialog_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(400)
        )
        
        # معلومات مفصلة
        details = [
            ("رقم الطلب", self.order_code),
            ("المنتج", self.product_name),
            ("الكمية", str(self.quantity)),
            ("السعر الإجمالي", f"{self.total_price} ريال"),
            ("التاريخ", self.order_date),
            ("الحالة", self.ids.status_chip.text),
            ("طريقة الدفع", self.order.get('payment_method', 'غير محدد')),
            ("عنوان التوصيل", self.order.get('delivery_address', 'غير محدد')),
        ]
        
        for label, value in details:
            row = MDBoxLayout(orientation='horizontal', adaptive_height=True)
            row.add_widget(MDLabel(
                text=f"{label}:",
                font_style='Body2',
                theme_text_color='Secondary',
                font_name='DroidArabic',
                size_hint_x=0.4
            ))
            row.add_widget(MDLabel(
                text=str(value),
                font_style='Body2',
                theme_text_color='Primary',
                font_name='DroidArabic',
                size_hint_x=0.6,
                halign='right'
            ))
            dialog_content.add_widget(row)
        
        # معلومات البائع إذا كانت متوفرة
        if self.order.get('seller_name'):
            seller_row = MDBoxLayout(orientation='horizontal', adaptive_height=True)
            seller_row.add_widget(MDLabel(
                text="البائع:",
                font_style='Body2',
                theme_text_color='Secondary',
                font_name='DroidArabic',
                size_hint_x=0.4
            ))
            seller_row.add_widget(MDLabel(
                text=self.order.get('seller_name'),
                font_style='Body2',
                theme_text_color='Primary',
                font_name='DroidArabic',
                size_hint_x=0.6,
                halign='right'
            ))
            dialog_content.add_widget(seller_row)
        
        # معلومات المندوب إذا كانت متوفرة
        if self.order.get('driver_name'):
            driver_row = MDBoxLayout(orientation='horizontal', adaptive_height=True)
            driver_row.add_widget(MDLabel(
                text="مندوب التوصيل:",
                font_style='Body2',
                theme_text_color='Secondary',
                font_name='DroidArabic',
                size_hint_x=0.4
            ))
            driver_row.add_widget(MDLabel(
                text=self.order.get('driver_name'),
                font_style='Body2',
                theme_text_color='Primary',
                font_name='DroidArabic',
                size_hint_x=0.6,
                halign='right'
            ))
            dialog_content.add_widget(driver_row)
        
        dialog = MDDialog(
            title="تفاصيل الطلب",
            type="custom",
            content_cls=dialog_content,
            buttons=[
                MDFlatButton(
                    text="إغلاق",
                    font_name='DroidArabic',
                    on_press=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

class OrdersScreen(Screen):
    """شاشة الطلبات"""
    
    orders = ListProperty([])
    filtered_orders = ListProperty([])
    current_filter = StringProperty('الكل')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = API()
        self.dialog = None
        Clock.schedule_once(self.load_orders)
    
    def on_enter(self):
        """عند دخول الشاشة"""
        self.load_orders()
    
    def load_orders(self, dt=None):
        """تحميل الطلبات"""
        app = self.manager.app
        if not app.user_data:
            self.show_empty_state("يرجى تسجيل الدخول لعرض الطلبات")
            return
        
        # في هذا الإصدار، نستخدم بيانات تجريبية
        # في الإصدار الكامل، سيتم جلبها من السيرفر
        self.orders = self.get_sample_orders()
        self.filter_orders(self.current_filter)
    
    def get_sample_orders(self):
        """الحصول على طلبات تجريبية"""
        return [
            {
                'id': 1,
                'order_code': 'ORD202401201230001',
                'product_name': 'قات صعدي ممتاز',
                'quantity': 2,
                'total_price': 120,
                'final_price': 220,  # مع الغسل
                'status': 'delivered',
                'created_at': '2024-01-20T12:30:00',
                'payment_method': 'محفظة جيب',
                'delivery_address': 'صنعاء - شارع الزبيري',
                'seller_name': 'مزرعة الصعدي',
                'driver_name': 'أحمد محمد'
            },
            {
                'id': 2,
                'order_code': 'ORD202401211445002',
                'product_name': 'قات همداني فاخر',
                'quantity': 1,
                'total_price': 55,
                'final_price': 55,
                'status': 'delivering',
                'created_at': '2024-01-21T14:45:00',
                'payment_method': 'رصيد الحساب',
                'delivery_address': 'تعز - وسط المدينة',
                'seller_name': 'محل الهمداني',
                'driver_name': 'محمد علي'
            },
            {
                'id': 3,
                'order_code': 'ORD202401220930003',
                'product_name': 'قات أرحبي طازج',
                'quantity': 3,
                'total_price': 135,
                'final_price': 235,  # مع الغسل
                'status': 'washing',
                'created_at': '2024-01-22T09:30:00',
                'payment_method': 'محفظة جوالي',
                'delivery_address': 'إب - وسط المحافظة',
                'seller_name': 'مزرعة أرحب'
            },
            {
                'id': 4,
                'order_code': 'ORD202401231130004',
                'product_name': 'قات حيوفي مميز',
                'quantity': 1,
                'total_price': 50,
                'final_price': 150,  # مع الغسل
                'status': 'preparing',
                'created_at': '2024-01-23T11:30:00',
                'payment_method': 'الدفع عند الاستلام',
                'delivery_address': 'الحديدة - الميناء'
            },
            {
                'id': 5,
                'order_code': 'ORD202401240815005',
                'product_name': 'قات روس فاخر',
                'quantity': 2,
                'total_price': 130,
                'final_price': 130,
                'status': 'pending',
                'created_at': '2024-01-24T08:15:00',
                'payment_method': 'محفظة موبايل موني',
                'delivery_address': 'صنعاء - شارع الستين'
            }
        ]
    
    def filter_orders(self, status_filter):
        """تصفية الطلبات حسب الحالة"""
        self.current_filter = status_filter
        
        if status_filter == 'الكل':
            self.filtered_orders = self.orders
        else:
            self.filtered_orders = [
                order for order in self.orders 
                if order.get('status') == status_filter
            ]
        
        self.display_orders()
    
    def display_orders(self):
        """عرض الطلبات"""
        container = self.ids.orders_container
        container.clear_widgets()
        
        if not self.filtered_orders:
            self.show_empty_state("لا توجد طلبات")
            return
        
        scroll = MDScrollView()
        orders_box = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(15),
            size_hint_y=None,
            adaptive_height=True
        )
        orders_box.bind(minimum_height=orders_box.setter('height'))
        
        for order in self.filtered_orders:
            card = OrderCard(order=order)
            orders_box.add_widget(card)
        
        scroll.add_widget(orders_box)
        container.add_widget(scroll)
    
    def show_empty_state(self, message):
        """عرض حالة فارغة"""
        container = self.ids.orders_container
        container.clear_widgets()
        
        empty_box = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(50),
            size_hint_y=None,
            height=dp(300),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        empty_box.add_widget(MDIconButton(
            icon="clipboard-text-outline",
            icon_size=dp(60),
            theme_icon_color="Secondary",
            pos_hint={'center_x': 0.5}
        ))
        
        empty_box.add_widget(MDLabel(
            text=message,
            font_style='H5',
            theme_text_color='Secondary',
            halign='center',
            font_name='DroidArabic'
        ))
        
        if message == "لا توجد طلبات":
            empty_box.add_widget(MDRaisedButton(
                text="تسوق الآن",
                font_name='DroidArabic',
                pos_hint={'center_x': 0.5},
                size_hint_x=0.6,
                on_press=lambda x: self.manager.current = 'products'
            ))
        
        container.add_widget(empty_box)
    
    def go_back(self):
        """العودة للشاشة السابقة"""
        self.manager.current = 'home'
    
    def create_new_order(self):
        """إنشاء طلب جديد"""
        self.manager.current = 'products'
    
    def show_error(self, message):
        """إظهار خطأ"""
        self.manager.app.show_error(message)
