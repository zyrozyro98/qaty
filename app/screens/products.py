# -*- coding: utf-8 -*-
"""
شاشة المنتجات - عرض وشراء المنتجات
"""
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.spinner import MDSpinner

from app.utils.arabic_support import ArabicSupport
from app.utils.api import API
from app.widgets.product_card import ProductCard

Builder.load_string('''
<CategoryChip>:
    orientation: 'horizontal'
    size_hint: None, None
    size: self.minimum_width, dp(40)
    padding: [dp(10), dp(5)]
    spacing: dp(5)
    radius: dp(20)
    elevation: 1 if not root.active else 2
    md_bg_color: [0.2, 0.7, 0.3, 1] if root.active else [0.9, 0.9, 0.9, 1]
    
    MDLabel:
        text: root.text
        font_style: 'Caption'
        theme_text_color: "Custom"
        text_color: [1, 1, 1, 1] if root.active else [0.3, 0.3, 0.3, 1]
        font_name: 'DroidArabic'
        bold: root.active
        size_hint_x: None
        width: self.texture_size[0]

<ProductsScreen>:
    MDScreen:
        md_bg_color: [0.95, 0.95, 0.95, 1]
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            
            # شريط البحث والتصفية
            MDCard:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(130)
                padding: dp(10)
                spacing: dp(10)
                elevation: 2
                radius: [0, 0, dp(15), dp(15)]
                
                # شريط البحث
                MDBoxLayout:
                    orientation: 'horizontal'
                    adaptive_height: True
                    spacing: dp(10)
                    
                    MDTextField:
                        id: search_input
                        hint_text: "بحث في المنتجات..."
                        mode: "rectangle"
                        size_hint_x: 0.8
                        font_name: 'DroidArabic'
                        text_direction: 'rtl'
                        on_text_validate: root.search_products()
                    
                    MDIconButton:
                        icon: "magnify"
                        on_press: root.search_products()
                
                # شريط التصنيفات
                ScrollView:
                    MDBoxLayout:
                        id: categories_container
                        orientation: 'horizontal'
                        spacing: dp(10)
                        size_hint_x: None
                        width: self.minimum_width
                        adaptive_width: True
                        height: dp(40)
                
                # خيارات التصفية
                MDBoxLayout:
                    orientation: 'horizontal'
                    adaptive_height: True
                    spacing: dp(10)
                    
                    MDFlatButton:
                        text: "فرز حسب"
                        icon: "sort"
                        font_name: 'DroidArabic'
                        on_press: root.show_sort_menu()
                    
                    MDFlatButton:
                        text: "تصفية"
                        icon: "filter"
                        font_name: 'DroidArabic'
                        on_press: root.show_filter_dialog()
            
            # عدد النتائج
            MDBoxLayout:
                orientation: 'horizontal'
                adaptive_height: True
                padding: [dp(20), 0]
                
                MDLabel:
                    id: results_count
                    text: "جاري التحميل..."
                    font_style: 'Body2'
                    theme_text_color: "Secondary"
                    font_name: 'DroidArabic'
                    halign: 'right'
                    size_hint_x: 1
                
                MDIconButton:
                    id: view_toggle
                    icon: "view-grid"
                    on_press: root.toggle_view()
            
            # قائمة المنتجات
            MDBoxLayout:
                orientation: 'vertical'
                id: products_container
''')

class CategoryChip(MDCard, ButtonBehavior):
    """شريط التصنيف"""
    text = StringProperty('')
    active = BooleanProperty(False)

class ProductsScreen(Screen):
    """شاشة المنتجات"""
    
    products = ListProperty([])
    filtered_products = ListProperty([])
    categories = ListProperty([])
    current_category = StringProperty('الكل')
    sort_by = StringProperty('الأحدث')
    view_mode = StringProperty('grid')  # grid أو list
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = API()
        self.sort_menu = None
        self.filter_dialog = None
        self.loading = False
        self.current_page = 1
        self.has_more = True
        Clock.schedule_once(self.setup_products)
    
    def on_enter(self):
        """عند دخول الشاشة"""
        self.load_products()
    
    def setup_products(self, dt):
        """إعداد شاشة المنتجات"""
        # إعداد التصنيفات الافتراضية
        self.categories = ['الكل', 'صعدي', 'همداني', 'أرحبي', 'حيوفي', 'نقفة', 'روس', 'عضوي']
        self.update_categories()
        
        # إعداد طريقة العرض
        self.view_mode = 'grid'
    
    def load_products(self, reset=True):
        """تحميل المنتجات"""
        if self.loading:
            return
        
        if reset:
            self.current_page = 1
            self.has_more = True
            self.products = []
        
        self.loading = True
        self.show_loading()
        
        # إعداد عوامل التصفية
        filters = {
            'page': self.current_page,
            'limit': 20
        }
        
        if self.current_category != 'الكل':
            filters['category'] = self.current_category
        
        # البحث إذا كان هناك نص بحث
        search_text = self.ids.search_input.text.strip()
        if search_text:
            filters['search'] = search_text
        
        # التصفية حسب السعر إذا تم تحديدها
        if hasattr(self, 'min_price_filter'):
            filters['min_price'] = self.min_price_filter
        
        if hasattr(self, 'max_price_filter'):
            filters['max_price'] = self.max_price_filter
        
        def on_success(response):
            self.hide_loading()
            self.loading = False
            
            if response.get('success'):
                new_products = response.get('products', [])
                
                if reset:
                    self.products = new_products
                else:
                    self.products.extend(new_products)
                
                # التحقق إذا كان هناك المزيد من المنتجات
                self.has_more = len(new_products) >= filters['limit']
                self.current_page += 1
                
                # تطبيق التصفية
                self.apply_filters()
                
                # تحديث عدد النتائج
                self.update_results_count()
                
                # عرض المنتجات
                self.display_products()
            else:
                self.show_error("فشل في تحميل المنتجات")
        
        def on_error(error):
            self.hide_loading()
            self.loading = False
            self.show_error("خطأ في الاتصال بالسيرفر")
        
        self.api.get_products(filters, on_success, on_error)
    
    def apply_filters(self):
        """تطبيق التصفيات"""
        self.filtered_products = self.products.copy()
        
        # التصفية حسب السعر
        if hasattr(self, 'min_price_filter'):
            self.filtered_products = [
                p for p in self.filtered_products 
                if p.get('price', 0) >= self.min_price_filter
            ]
        
        if hasattr(self, 'max_price_filter'):
            self.filtered_products = [
                p for p in self.filtered_products 
                if p.get('price', 0) <= self.max_price_filter
            ]
        
        # الفرز
        if self.sort_by == 'الأحدث':
            self.filtered_products.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif self.sort_by == 'الأقدم':
            self.filtered_products.sort(key=lambda x: x.get('created_at', ''))
        elif self.sort_by == 'الأعلى سعراً':
            self.filtered_products.sort(key=lambda x: x.get('price', 0), reverse=True)
        elif self.sort_by == 'الأقل سعراً':
            self.filtered_products.sort(key=lambda x: x.get('price', 0))
        elif self.sort_by == 'الأعلى تقييماً':
            self.filtered_products.sort(key=lambda x: x.get('rating', 0), reverse=True)
    
    def display_products(self):
        """عرض المنتجات"""
        container = self.ids.products_container
        container.clear_widgets()
        
        if not self.filtered_products:
            # لا توجد منتجات
            empty_box = MDBoxLayout(
                orientation='vertical',
                spacing=dp(20),
                padding=dp(50),
                size_hint_y=None,
                height=dp(300),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            
            empty_box.add_widget(MDLabel(
                text="لا توجد منتجات",
                font_style='H5',
                theme_text_color='Secondary',
                halign='center',
                font_name='DroidArabic'
            ))
            
            empty_box.add_widget(MDLabel(
                text="جرب تغيير معايير البحث أو التصفية",
                font_style='Body1',
                theme_text_color='Hint',
                halign='center',
                font_name='DroidArabic'
            ))
            
            container.add_widget(empty_box)
            return
        
        if self.view_mode == 'grid':
            # عرض شبكي
            scroll = MDScrollView()
            grid = MDGridLayout(
                cols=2,
                spacing=dp(15),
                padding=dp(15),
                size_hint_y=None,
                adaptive_height=True
            )
            grid.bind(minimum_height=grid.setter('height'))
            
            for product in self.filtered_products:
                card = ProductCard(
                    product=product,
                    size_hint=(None, None),
                    size=(dp(165), dp(280)),
                    on_buy=lambda p=product: self.buy_product(p)
                )
                grid.add_widget(card)
            
            # زر تحميل المزيد
            if self.has_more:
                load_more_btn = MDRaisedButton(
                    text="تحميل المزيد",
                    size_hint=(None, None),
                    size=(dp(150), dp(40)),
                    pos_hint={'center_x': 0.5},
                    font_name='DroidArabic',
                    on_press=lambda x: self.load_products(reset=False)
                )
                grid.add_widget(load_more_btn)
            
            scroll.add_widget(grid)
            container.add_widget(scroll)
        
        else:
            # عرض قائمي
            scroll = MDScrollView()
            list_layout = MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                padding=dp(15),
                size_hint_y=None,
                adaptive_height=True
            )
            list_layout.bind(minimum_height=list_layout.setter('height'))
            
            for product in self.filtered_products:
                card = MDCard(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(120),
                    padding=dp(10),
                    spacing=dp(10),
                    elevation=1,
                    radius=dp(10)
                )
                
                # صورة المنتج
                img_box = MDBoxLayout(
                    size_hint_x=None,
                    width=dp(100),
                    radius=dp(5)
                )
                # هنا يمكن إضافة صورة
                card.add_widget(img_box)
                
                # معلومات المنتج
                info_box = MDBoxLayout(
                    orientation='vertical',
                    spacing=dp(5)
                )
                
                info_box.add_widget(MDLabel(
                    text=product.get('name', ''),
                    font_style='Subtitle1',
                    theme_text_color='Primary',
                    font_name='DroidArabic',
                    bold=True,
                    size_hint_y=None,
                    height=dp(30)
                ))
                
                info_box.add_widget(MDLabel(
                    text=product.get('description', '')[:50] + '...',
                    font_style='Body2',
                    theme_text_color='Secondary',
                    font_name='DroidArabic',
                    size_hint_y=None,
                    height=dp(25)
                ))
                
                info_box.add_widget(MDLabel(
                    text=f"{product.get('price', 0)} ريال",
                    font_style='H6',
                    theme_text_color='Primary',
                    font_name='DroidArabic',
                    bold=True,
                    size_hint_y=None,
                    height=dp(30)
                ))
                
                card.add_widget(info_box)
                
                # زر الشراء
                buy_btn = MDRaisedButton(
                    text="شراء",
                    size_hint_x=None,
                    width=dp(80),
                    font_name='DroidArabic',
                    on_press=lambda x, p=product: self.buy_product(p)
                )
                card.add_widget(buy_btn)
                
                list_layout.add_widget(card)
            
            scroll.add_widget(list_layout)
            container.add_widget(scroll)
    
    def update_categories(self):
        """تحديث شريط التصنيفات"""
        container = self.ids.categories_container
        container.clear_widgets()
        
        for category in self.categories:
            chip = CategoryChip(
                text=category,
                active=(category == self.current_category)
            )
            chip.bind(on_press=lambda x, c=category: self.select_category(c))
            container.add_widget(chip)
    
    def select_category(self, category):
        """اختيار تصنيف"""
        self.current_category = category
        self.update_categories()
        self.load_products()
    
    def search_products(self):
        """بحث في المنتجات"""
        self.load_products()
    
    def show_sort_menu(self):
        """عرض قائمة الفرز"""
        sort_options = [
            {
                "text": "الأحدث",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="الأحدث": self.set_sort_by(x),
            },
            {
                "text": "الأقدم",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="الأقدم": self.set_sort_by(x),
            },
            {
                "text": "الأعلى سعراً",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="الأعلى سعراً": self.set_sort_by(x),
            },
            {
                "text": "الأقل سعراً",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="الأقل سعراً": self.set_sort_by(x),
            },
            {
                "text": "الأعلى تقييماً",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="الأعلى تقييماً": self.set_sort_by(x),
            },
        ]
        
        self.sort_menu = MDDropdownMenu(
            caller=self.ids.view_toggle.parent.children[1],  # زر الفرز
            items=sort_options,
            width_mult=4,
            max_height=dp(250),
        )
        self.sort_menu.open()
    
    def set_sort_by(self, sort_by):
        """تعيين طريقة الفرز"""
        self.sort_by = sort_by
        if self.sort_menu:
            self.sort_menu.dismiss()
        
        self.apply_filters()
        self.display_products()
    
    def show_filter_dialog(self):
        """عرض نافذة التصفية"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(300)
        )
        
        # تصفية السعر
        content.add_widget(MDLabel(
            text="نطاق السعر",
            font_style='Subtitle1',
            theme_text_color='Primary',
            font_name='DroidArabic',
            bold=True
        ))
        
        price_box = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        min_price = MDTextField(
            hint_text="الحد الأدنى",
            mode="rectangle",
            font_name='DroidArabic',
            input_type='number'
        )
        price_box.add_widget(min_price)
        
        max_price = MDTextField(
            hint_text="الحد الأقصى",
            mode="rectangle",
            font_name='DroidArabic',
            input_type='number'
        )
        price_box.add_widget(max_price)
        
        content.add_widget(price_box)
        
        # تصفية حسب البائع
        content.add_widget(MDLabel(
            text="البائع",
            font_style='Subtitle1',
            theme_text_color='Primary',
            font_name='DroidArabic',
            bold=True
        ))
        
        seller_check = MDCheckbox(
            size_hint_x=None,
            width=dp(40)
        )
        
        seller_box = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        seller_box.add_widget(MDLabel(
            text="عرض منتجات البائعين المميزين فقط",
            font_style='Body2',
            theme_text_color='Secondary',
            font_name='DroidArabic',
            size_hint_x=1
        ))
        seller_box.add_widget(seller_check)
        
        content.add_widget(seller_box)
        
        # أزرار التصفية
        buttons_box = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        def apply_filter(instance):
            try:
                if min_price.text:
                    self.min_price_filter = float(min_price.text)
                if max_price.text:
                    self.max_price_filter = float(max_price.text)
                
                self.filter_dialog.dismiss()
                self.load_products()
            except ValueError:
                self.show_error("يرجى إدخال أرقام صحيحة")
        
        apply_btn = MDRaisedButton(
            text="تطبيق",
            font_name='DroidArabic',
            on_press=apply_filter
        )
        
        reset_btn = MDFlatButton(
            text="إعادة تعيين",
            font_name='DroidArabic',
            on_press=lambda x: self.reset_filters()
        )
        
        buttons_box.add_widget(apply_btn)
        buttons_box.add_widget(reset_btn)
        content.add_widget(buttons_box)
        
        self.filter_dialog = MDDialog(
            title="تصفية المنتجات",
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),
            height=dp(450)
        )
        self.filter_dialog.open()
    
    def reset_filters(self):
        """إعادة تعيين التصفيات"""
        if hasattr(self, 'min_price_filter'):
            delattr(self, 'min_price_filter')
        if hasattr(self, 'max_price_filter'):
            delattr(self, 'max_price_filter')
        
        if self.filter_dialog:
            self.filter_dialog.dismiss()
        
        self.load_products()
    
    def toggle_view(self):
        """تبديل طريقة العرض"""
        self.view_mode = 'list' if self.view_mode == 'grid' else 'grid'
        self.ids.view_toggle.icon = "view-list" if self.view_mode == 'grid' else "view-grid"
        self.display_products()
    
    def buy_product(self, product):
        """شراء منتج"""
        app = self.manager.app
        if not app.user_data:
            self.show_error("يرجى تسجيل الدخول أولاً")
            self.manager.current = 'login'
            return
        
        # فتح نافذة الشراء
        from app.screens.cart import BuyDialog
        buy_dialog = BuyDialog(product=product)
        buy_dialog.open()
    
    def update_results_count(self):
        """تحديث عدد النتائج"""
        count = len(self.filtered_products)
        self.ids.results_count.text = f"عرض {count} منتج"
    
    def show_loading(self):
        """إظهار مؤشر التحميل"""
        container = self.ids.products_container
        container.clear_widgets()
        
        loading_box = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(50),
            size_hint_y=None,
            height=dp(200),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            active=True
        )
        loading_box.add_widget(spinner)
        
        loading_box.add_widget(MDLabel(
            text="جاري تحميل المنتجات...",
            font_style='Body1',
            theme_text_color='Secondary',
            halign='center',
            font_name='DroidArabic'
        ))
        
        container.add_widget(loading_box)
    
    def hide_loading(self):
        """إخفاء مؤشر التحميل"""
        pass
    
    def show_error(self, message):
        """إظهار خطأ"""
        self.manager.app.show_error(message)
