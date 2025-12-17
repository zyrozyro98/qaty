# -*- coding: utf-8 -*-
"""
لوحة تحكم المدير - شاشة إدارة كاملة
"""
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDFabButton, MDIconButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.floatlayout import MDFloatLayout

from app.utils.arabic_support import ArabicSupport
from app.utils.api import API

Builder.load_string('''
<AdminTab>:
    MDLabel:
        text: root.text
        halign: 'center'

<StatCard@MDCard>:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(5)
    size_hint: None, None
    size: dp(160), dp(110)
    elevation: 2
    radius: dp(10)
    
    MDLabel:
        text: root.title
        font_style: 'Caption'
        theme_text_color: "Secondary"
        halign: 'center'
        font_name: 'DroidArabic'
        size_hint_y: None
        height: dp(20)
    
    MDLabel:
        text: root.value
        font_style: 'H6'
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
        height: dp(20)

<AdminDashboardScreen>:
    MDScreen:
        md_bg_color: [0.95, 0.95, 0.95, 1]
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: 0
            
            # شريط العنوان
            MDBoxLayout:
                orientation: 'horizontal'
                adaptive_height: True
                padding: dp(10)
                md_bg_color: app.theme_cls.primary_color
                
                MDIconButton:
                    icon: "arrow-left"
                    theme_icon_color: "Custom"
                    icon_color: [1, 1, 1, 1]
                    on_release: root.go_back()
                
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(2)
                    
                    MDLabel:
                        text: "لوحة تحكم المدير"
                        font_style: 'H6'
                        theme_text_color: "Custom"
                        text_color: [1, 1, 1, 1]
                        font_name: 'DroidArabic'
                        bold: True
                        size_hint_y: None
                        height: dp(30)
                    
                    MDLabel:
                        id: welcome_label
                        text: ""
                        font_style: 'Body2'
                        theme_text_color: "Custom"
                        text_color: [1, 1, 1, 0.8]
                        font_name: 'DroidArabic'
                        size_hint_y: None
                        height: dp(20)
                
                MDIconButton:
                    icon: "refresh"
                    theme_icon_color: "Custom"
                    icon_color: [1, 1, 1, 1]
                    on_release: root.refresh_data()
                
                MDIconButton:
                    icon: "cog"
                    theme_icon_color: "Custom"
                    icon_color: [1, 1, 1, 1]
                    on_release: root.show_settings()
            
            # علامات التبويب
            MDTabs:
                id: tabs
                on_tab_switch: root.on_tab_switch(*args)
                tab_hint_x: True
                
                AdminTab:
                    text: "لوحة التحكم"
                    icon: "view-dashboard"
                
                AdminTab:
                    text: "المستخدمين"
                    icon: "account-group"
                
                AdminTab:
                    text: "المنتجات"
                    icon: "store"
                
                AdminTab:
                    text: "الطلبات"
                    icon: "clipboard-list"
                
                AdminTab:
                    text: "المحفظة"
                    icon: "wallet"
                
                AdminTab:
                    text: "الإعدادات"
                    icon: "cog"
            
            # محتوى علامات التبويب
            MDBoxLayout:
                id: tab_content
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
''')

class AdminTab(MDFloatLayout, MDTabsBase):
    """علامة تبويب لوحة التحكم"""
    pass

class StatCard(MDCard):
    """بطاقة إحصائية"""
    title = StringProperty('')
    value = StringProperty('')
    subtitle = StringProperty('')

class AdminDashboardScreen(Screen):
    """لوحة تحكم المدير"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.api = API()
        self.current_tab = 'dashboard'
        Clock.schedule_once(self.setup_admin_dashboard)
    
    def setup_admin_dashboard(self, dt):
        """إعداد لوحة التحكم"""
        self.update_welcome_message()
        self.load_dashboard_stats()
    
    def on_enter(self):
        """عند دخول الشاشة"""
        self.update_welcome_message()
        if self.current_tab == 'dashboard':
            self.load_dashboard_stats()
    
    def update_welcome_message(self):
        """تحديث رسالة الترحيب"""
        app = self.manager.app
        if app.user_data:
            name = app.user_data.get('full_name', 'مدير النظام')
            self.ids.welcome_label.text = f"مرحباً {name}"
    
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        """عند تغيير علامة التبويب"""
        self.current_tab = tab_text
        
        # مسح المحتوى القديم
        tab_content = self.ids.tab_content
        tab_content.clear_widgets()
        
        # تحميل المحتوى المناسب
        if tab_text == 'لوحة التحكم':
            self.load_dashboard_content()
        elif tab_text == 'المستخدمين':
            self.load_users_content()
        elif tab_text == 'المنتجات':
            self.load_products_content()
        elif tab_text == 'الطلبات':
            self.load_orders_content()
        elif tab_text == 'المحفظة':
            self.load_wallet_content()
        elif tab_text == 'الإعدادات':
            self.load_settings_content()
    
    def load_dashboard_content(self):
        """تحميل محتوى لوحة التحكم"""
        tab_content = self.ids.tab_content
        
        # زر التهيئة للنظام الجديد
        init_btn = MDRaisedButton(
            text="تهيئة النظام ببيانات أولية",
            size_hint_x=1,
            height=dp(50),
            font_name='DroidArabic',
            on_release=self.init_system
        )
        tab_content.add_widget(init_btn)
        
        # إحصائيات سريعة
        stats_label = MDLabel(
            text="الإحصائيات السريعة",
            font_style='H6',
            theme_text_color="Primary",
            halign='right',
            font_name='DroidArabic',
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        tab_content.add_widget(stats_label)
        
        # شبكة الإحصائيات
        stats_grid = MDGridLayout(
            cols=3,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(250),
            adaptive_height=True
        )
        
        # بطاقات إحصائية (سيتم تحديثها بالبيانات الحقيقية)
        self.stat_cards = {}
        
        stats_data = [
            ('المستخدمين', '0', 'إجمالي المسجلين'),
            ('البائعين', '0', 'إجمالي البائعين'),
            ('المشترين', '0', 'إجمالي المشترين'),
            ('المنتجات', '0', 'المنتجات المتاحة'),
            ('الطلبات', '0', 'إجمالي الطلبات'),
            ('المبيعات', '0 ريال', 'إجمالي المبيعات'),
        ]
        
        for title, value, subtitle in stats_data:
            card = StatCard(
                title=title,
                value=value,
                subtitle=subtitle
            )
            self.stat_cards[title] = card
            stats_grid.add_widget(card)
        
        tab_content.add_widget(stats_grid)
        
        # تحميل الإحصائيات الحقيقية
        self.load_dashboard_stats()
    
    def load_dashboard_stats(self):
        """تحميل إحصائيات لوحة التحكم"""
        app = self.manager.app
        token = app.user_token
        
        def on_success(response):
            if response.get('success'):
                stats = response.get('stats', {})
                
                # تحديث بطاقات الإحصائيات
                if hasattr(self, 'stat_cards'):
                    users_stats = stats.get('users', {})
                    products_stats = stats.get('products', {})
                    orders_stats = stats.get('orders', {})
                    
                    if 'المستخدمين' in self.stat_cards:
                        self.stat_cards['المستخدمين'].value = str(users_stats.get('total', 0))
                    
                    if 'البائعين' in self.stat_cards:
                        self.stat_cards['البائعين'].value = str(users_stats.get('sellers', 0))
                    
                    if 'المشترين' in self.stat_cards:
                        self.stat_cards['المشترين'].value = str(users_stats.get('buyers', 0))
                    
                    if 'المنتجات' in self.stat_cards:
                        self.stat_cards['المنتجات'].value = str(products_stats.get('available', 0))
                    
                    if 'الطلبات' in self.stat_cards:
                        self.stat_cards['الطلبات'].value = str(orders_stats.get('total', 0))
                    
                    if 'المبيعات' in self.stat_cards:
                        total_sales = orders_stats.get('total_sales', 0)
                        self.stat_cards['المبيعات'].value = f"{total_sales:,.0f} ريال"
        
        def on_error(error):
            app.show_error("خطأ في جلب الإحصائيات")
        
        if token:
            self.api.make_request(
                '/admin/dashboard/stats',
                {},
                on_success,
                on_error,
                method='GET',
                headers={'Authorization': f'Bearer {token}'}
            )
    
    def load_users_content(self):
        """تحميل محتوى إدارة المستخدمين"""
        tab_content = self.ids.tab_content
        
        # شريط البحث والإجراءات
        action_bar = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        # حقل البحث
        search_input = MDTextField(
            hint_text="بحث عن مستخدم...",
            mode="rectangle",
            size_hint_x=0.6,
            font_name='DroidArabic'
        )
        action_bar.add_widget(search_input)
        
        # زر البحث
        search_btn = MDIconButton(
            icon="magnify",
            on_release=lambda x: self.search_users(search_input.text)
        )
        action_bar.add_widget(search_btn)
        
        # زر إضافة مستخدم
        add_btn = MDIconButton(
            icon="plus",
            on_release=self.show_add_user_dialog
        )
        action_bar.add_widget(add_btn)
        
        tab_content.add_widget(action_bar)
        
        # قائمة المستخدمين
        scroll = MDScrollView()
        self.users_list = MDList()
        scroll.add_widget(self.users_list)
        tab_content.add_widget(scroll)
        
        # تحميل المستخدمين
        self.load_users()
    
    def load_users(self):
        """تحميل قائمة المستخدمين"""
        app = self.manager.app
        token = app.user_token
        
        def on_success(response):
            if response.get('success'):
                users = response.get('users', [])
                self.display_users(users)
        
        def on_error(error):
            app.show_error("خطأ في جلب المستخدمين")
        
        if token:
            self.api.make_request(
                '/admin/users',
                {},
                on_success,
                on_error,
                method='GET',
                headers={'Authorization': f'Bearer {token}'}
            )
    
    def display_users(self, users):
        """عرض قائمة المستخدمين"""
        self.users_list.clear_widgets()
        
        for user in users:
            item = ThreeLineListItem(
                text=user.get('full_name', ''),
                secondary_text=f"اسم المستخدم: {user.get('username', '')}",
                tertiary_text=f"الدور: {user.get('role', '')} | الهاتف: {user.get('phone', '')}",
                font_name='DroidArabic',
                on_release=lambda x, u=user: self.show_user_details(u)
            )
            self.users_list.add_widget(item)
    
    def show_user_details(self, user):
        """عرض تفاصيل المستخدم"""
        dialog_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(300)
        )
        
        # معلومات المستخدم
        info_text = f"""
        الاسم: {user.get('full_name', '')}
        اسم المستخدم: {user.get('username', '')}
        البريد: {user.get('email', '')}
        الهاتف: {user.get('phone', '')}
        الدور: {user.get('role', '')}
        الرصيد: {user.get('wallet_balance', 0)} ريال
        """
        
        dialog_content.add_widget(MDLabel(
            text=info_text,
            font_name='DroidArabic',
            halign='right'
        ))
        
        # أزرار الإجراءات
        actions = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        edit_btn = MDRaisedButton(
            text="تعديل",
            size_hint_x=0.33,
            font_name='DroidArabic',
            on_release=lambda x: self.edit_user(user)
        )
        actions.add_widget(edit_btn)
        
        if user.get('role') != 'admin':  # لا يمكن حذف المدير
            delete_btn = MDRaisedButton(
                text="حذف",
                size_hint_x=0.33,
                font_name='DroidArabic',
                on_release=lambda x: self.delete_user(user)
            )
            actions.add_widget(delete_btn)
        
        close_btn = MDFlatButton(
            text="إغلاق",
            size_hint_x=0.33,
            font_name='DroidArabic',
            on_release=lambda x: self.dialog.dismiss()
        )
        actions.add_widget(close_btn)
        
        dialog_content.add_widget(actions)
        
        self.dialog = MDDialog(
            title=ArabicSupport.arabic_text(f"تفاصيل المستخدم: {user.get('full_name', '')}"),
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.6)
        )
        self.dialog.open()
    
    def show_add_user_dialog(self, instance):
        """عرض نافذة إضافة مستخدم جديد"""
        dialog_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(450)
        )
        
        # حقول الإدخال
        fields = [
            ('full_name', 'الاسم الكامل', 'text'),
            ('username', 'اسم المستخدم', 'text'),
            ('email', 'البريد الإلكتروني', 'email'),
            ('phone', 'رقم الهاتف', 'tel'),
            ('password', 'كلمة المرور', 'password'),
            ('role', 'الدور', 'dropdown'),
            ('store_name', 'اسم المتجر (للبائعين)', 'text'),
            ('vehicle_type', 'نوع المركبة (لمندوبي التوصيل)', 'text'),
            ('wallet_balance', 'الرصيد الابتدائي', 'number')
        ]
        
        self.user_fields = {}
        
        for field_name, hint, field_type in fields:
            if field_type == 'dropdown':
                # قائمة منسدلة للدور
                role_layout = MDBoxLayout(
                    orientation='horizontal',
                    spacing=dp(10),
                    size_hint_y=None,
                    height=dp(50)
                )
                
                role_layout.add_widget(MDLabel(
                    text="الدور:",
                    size_hint_x=0.3,
                    font_name='DroidArabic'
                ))
                
                role_input = MDTextField(
                    hint_text="اختر الدور",
                    mode="rectangle",
                    size_hint_x=0.7,
                    font_name='DroidArabic'
                )
                
                # قائمة الأدوار
                roles_menu = MDDropdownMenu(
                    caller=role_input,
                    items=[
                        {"text": "مشتري", "viewclass": "OneLineListItem", 
                         "on_release": lambda x="buyer": set_role(x)},
                        {"text": "بائع", "viewclass": "OneLineListItem", 
                         "on_release": lambda x="seller": set_role(x)},
                        {"text": "مندوب توصيل", "viewclass": "OneLineListItem", 
                         "on_release": lambda x="driver": set_role(x)},
                        {"text": "مدير", "viewclass": "OneLineListItem", 
                         "on_release": lambda x="admin": set_role(x)}
                    ]
                )
                
                def set_role(role):
                    role_input.text = role
                    roles_menu.dismiss()
                
                role_input.bind(on_focus=lambda instance, value: roles_menu.open() if value else None)
                self.user_fields[field_name] = role_input
                role_layout.add_widget(role_input)
                dialog_content.add_widget(role_layout)
                
            else:
                field = MDTextField(
                    hint_text=hint,
                    mode="rectangle",
                    size_hint_y=None,
                    height=dp(50),
                    font_name='DroidArabic'
                )
                
                if field_type == 'password':
                    field.password = True
                elif field_type == 'number':
                    field.input_filter = 'float'
                
                self.user_fields[field_name] = field
                dialog_content.add_widget(field)
        
        # أزرار الإجراءات
        actions = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        def add_user(instance):
            user_data = {}
            for field_name, field in self.user_fields.items():
                user_data[field_name] = field.text
            
            # التحقق من البيانات
            required_fields = ['full_name', 'username', 'email', 'phone', 'password', 'role']
            for field in required_fields:
                if not user_data.get(field):
                    app = self.manager.app
                    app.show_error(f"حقل {field} مطلوب")
                    return
            
            self.create_user(user_data)
            self.dialog.dismiss()
        
        add_btn = MDRaisedButton(
            text="إضافة",
            size_hint_x=0.5,
            font_name='DroidArabic',
            on_release=add_user
        )
        actions.add_widget(add_btn)
        
        cancel_btn = MDFlatButton(
            text="إلغاء",
            size_hint_x=0.5,
            font_name='DroidArabic',
            on_release=lambda x: self.dialog.dismiss()
        )
        actions.add_widget(cancel_btn)
        
        dialog_content.add_widget(actions)
        
        self.dialog = MDDialog(
            title=ArabicSupport.arabic_text("إضافة مستخدم جديد"),
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.8)
        )
        self.dialog.open()
    
    def create_user(self, user_data):
        """إنشاء مستخدم جديد"""
        app = self.manager.app
        token = app.user_token
        
        def on_success(response):
            if response.get('success'):
                app.show_success("تم إنشاء المستخدم بنجاح")
                self.load_users()  # تحديث القائمة
            else:
                app.show_error(response.get('message', 'خطأ في إنشاء المستخدم'))
        
        def on_error(error):
            app.show_error("خطأ في الاتصال بالسيرفر")
        
        if token:
            self.api.make_request(
                '/admin/users',
                user_data,
                on_success,
                on_error,
                method='POST',
                headers={'Authorization': f'Bearer {token}'}
            )
    
    def edit_user(self, user):
        """تعديل بيانات المستخدم"""
        # سيتم تنفيذها لاحقاً
        pass
    
    def delete_user(self, user):
        """حذف مستخدم"""
        app = self.manager.app
        
        def confirm_delete(instance):
            token = app.user_token
            
            def on_success(response):
                if response.get('success'):
                    app.show_success("تم حذف المستخدم بنجاح")
                    self.load_users()  # تحديث القائمة
                else:
                    app.show_error(response.get('message', 'خطأ في حذف المستخدم'))
            
            def on_error(error):
                app.show_error("خطأ في الاتصال بالسيرفر")
            
            if token:
                self.api.make_request(
                    f'/admin/users/{user["id"]}',
                    {},
                    on_success,
                    on_error,
                    method='DELETE',
                    headers={'Authorization': f'Bearer {token}'}
                )
            
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title=ArabicSupport.arabic_text("تأكيد الحذف"),
            text=ArabicSupport.arabic_text(f"هل أنت متأكد من حذف المستخدم {user.get('full_name', '')}؟"),
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    font_name='DroidArabic',
                    on_press=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="حذف",
                    font_name='DroidArabic',
                    on_press=confirm_delete
                )
            ]
        )
        self.dialog.open()
    
    def search_users(self, query):
        """بحث عن مستخدمين"""
        if query:
            # سيتم تنفيذ البحث لاحقاً
            pass
    
    def load_products_content(self):
        """تحميل محتوى إدارة المنتجات"""
        tab_content = self.ids.tab_content
        
        label = MDLabel(
            text="إدارة المنتجات - قريباً",
            font_style='H6',
            theme_text_color="Primary",
            halign='center',
            font_name='DroidArabic',
            valign='middle'
        )
        tab_content.add_widget(label)
    
    def load_orders_content(self):
        """تحميل محتوى إدارة الطلبات"""
        tab_content = self.ids.tab_content
        
        label = MDLabel(
            text="إدارة الطلبات - قريباً",
            font_style='H6',
            theme_text_color="Primary",
            halign='center',
            font_name='DroidArabic',
            valign='middle'
        )
        tab_content.add_widget(label)
    
    def load_wallet_content(self):
        """تحميل محتوى إدارة المحفظة"""
        tab_content = self.ids.tab_content
        
        label = MDLabel(
            text="إدارة المحفظة - قريباً",
            font_style='H6',
            theme_text_color="Primary",
            halign='center',
            font_name='DroidArabic',
            valign='middle'
        )
        tab_content.add_widget(label)
    
    def load_settings_content(self):
        """تحميل محتوى الإعدادات"""
        tab_content = self.ids.tab_content
        
        # إعدادات النظام
        settings_label = MDLabel(
            text="إعدادات النظام",
            font_style='H6',
            theme_text_color="Primary",
            halign='right',
            font_name='DroidArabic',
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        tab_content.add_widget(settings_label)
        
        # زر إدارة الأسواق
        markets_btn = MDRaisedButton(
            text="إدارة الأسواق",
            size_hint_x=1,
            height=dp(50),
            font_name='DroidArabic',
            on_release=self.manage_markets
        )
        tab_content.add_widget(markets_btn)
        
        # زر إدارة المغاسل
        washers_btn = MDRaisedButton(
            text="إدارة مغاسل القات",
            size_hint_x=1,
            height=dp(50),
            font_name='DroidArabic',
            on_release=self.manage_washers
        )
        tab_content.add_widget(washers_btn)
        
        # زر إدارة باقات الإعلانات
        ad_packages_btn = MDRaisedButton(
            text="إدارة باقات الإعلانات",
            size_hint_x=1,
            height=dp(50),
            font_name='DroidArabic',
            on_release=self.manage_ad_packages
        )
        tab_content.add_widget(ad_packages_btn)
        
        # زر إنشاء أكواد هدايا
        gift_codes_btn = MDRaisedButton(
            text="إنشاء أكواد هدايا",
            size_hint_x=1,
            height=dp(50),
            font_name='DroidArabic',
            on_release=self.create_gift_codes
        )
        tab_content.add_widget(gift_codes_btn)
        
        # إدارة طلبات السحب
        withdrawals_btn = MDRaisedButton(
            text="إدارة طلبات السحب",
            size_hint_x=1,
            height=dp(50),
            font_name='DroidArabic',
            on_release=self.manage_withdrawals
        )
        tab_content.add_widget(withdrawals_btn)
    
    def init_system(self, instance):
        """تهيئة النظام ببيانات أولية"""
        app = self.manager.app
        token = app.user_token
        
        def on_success(response):
            if response.get('success'):
                data = response.get('data', {})
                message = f"""
                تم تهيئة النظام بنجاح:
                • الأسواق: {data.get('markets_created', 0)}
                • المغاسل: {data.get('washers_created', 0)}
                • الباقات: {data.get('packages_created', 0)}
                • المستخدمون: {data.get('users_created', 0)}
                """
                app.show_success(message)
                self.load_dashboard_stats()  # تحديث الإحصائيات
            else:
                app.show_error(response.get('message', 'خطأ في تهيئة النظام'))
        
        def on_error(error):
            app.show_error("خطأ في الاتصال بالسيرفر")
        
        if token:
            self.api.make_request(
                '/admin/system/init',
                {},
                on_success,
                on_error,
                method='POST',
                headers={'Authorization': f'Bearer {token}'}
            )
    
    def manage_markets(self, instance):
        """إدارة الأسواق"""
        app = self.manager.app
        app.show_success("قريباً: إدارة الأسواق")
    
    def manage_washers(self, instance):
        """إدارة مغاسل القات"""
        app = self.manager.app
        app.show_success("قريباً: إدارة مغاسل القات")
    
    def manage_ad_packages(self, instance):
        """إدارة باقات الإعلانات"""
        app = self.manager.app
        app.show_success("قريباً: إدارة باقات الإعلانات")
    
    def create_gift_codes(self, instance):
        """إنشاء أكواد هدايا"""
        dialog_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(250)
        )
        
        # حقل المبلغ
        amount_input = MDTextField(
            hint_text="المبلغ لكل كود (ريال)",
            mode="rectangle",
            size_hint_y=None,
            height=dp(50),
            font_name='DroidArabic',
            input_filter='float'
        )
        dialog_content.add_widget(amount_input)
        
        # حقل العدد
        count_input = MDTextField(
            hint_text="عدد الأكواد",
            mode="rectangle",
            size_hint_y=None,
            height=dp(50),
            font_name='DroidArabic',
            input_filter='int'
        )
        dialog_content.add_widget(count_input)
        
        # حقل مدة الصلاحية
        expires_input = MDTextField(
            hint_text="مدة الصلاحية (أيام)",
            mode="rectangle",
            size_hint_y=None,
            height=dp(50),
            font_name='DroidArabic',
            input_filter='int',
            text="30"
        )
        dialog_content.add_widget(expires_input)
        
        # أزرار الإجراءات
        actions = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        def create_codes(instance):
            amount = amount_input.text
            count = count_input.text
            expires_days = expires_input.text
            
            if not amount or not count:
                app = self.manager.app
                app.show_error("يرجى إدخال المبلغ والعدد")
                return
            
            self.create_gift_codes_request(float(amount), int(count), int(expires_days))
            self.dialog.dismiss()
        
        create_btn = MDRaisedButton(
            text="إنشاء",
            size_hint_x=0.5,
            font_name='DroidArabic',
            on_release=create_codes
        )
        actions.add_widget(create_btn)
        
        cancel_btn = MDFlatButton(
            text="إلغاء",
            size_hint_x=0.5,
            font_name='DroidArabic',
            on_release=lambda x: self.dialog.dismiss()
        )
        actions.add_widget(cancel_btn)
        
        dialog_content.add_widget(actions)
        
        self.dialog = MDDialog(
            title=ArabicSupport.arabic_text("إنشاء أكواد هدايا"),
            type="custom",
            content_cls=dialog_content,
            size_hint=(0.9, 0.5)
        )
        self.dialog.open()
    
    def create_gift_codes_request(self, amount, count, expires_days):
        """إنشاء أكواد هدايا عبر API"""
        app = self.manager.app
        token = app.user_token
        
        def on_success(response):
            if response.get('success'):
                codes = response.get('codes', [])
                message = f"""
                تم إنشاء {count} كود هدية:
                المبلغ: {amount} ريال لكل كود
                الصلاحية: {expires_days} يوم
                
                الأكواد:
                {', '.join(codes[:5])}
                """
                if len(codes) > 5:
                    message += f"\nو {len(codes) - 5} كود آخر..."
                
                app.show_success(message)
            else:
                app.show_error(response.get('message', 'خطأ في إنشاء الأكواد'))
        
        def on_error(error):
            app.show_error("خطأ في الاتصال بالسيرفر")
        
        if token:
            data = {
                'amount': amount,
                'count': count,
                'expires_days': expires_days
            }
            
            self.api.make_request(
                '/admin/gift-codes',
                data,
                on_success,
                on_error,
                method='POST',
                headers={'Authorization': f'Bearer {token}'}
            )
    
    def manage_withdrawals(self, instance):
        """إدارة طلبات السحب"""
        app = self.manager.app
        app.show_success("قريباً: إدارة طلبات السحب")
    
    def show_settings(self):
        """عرض إعدادات المدير"""
        app = self.manager.app
        app.show_success("قريباً: إعدادات المدير")
    
    def refresh_data(self):
        """تحديث البيانات"""
        if self.current_tab == 'لوحة التحكم':
            self.load_dashboard_stats()
        elif self.current_tab == 'المستخدمين':
            self.load_users()
        
        app = self.manager.app
        app.show_success("تم تحديث البيانات")
    
    def go_back(self):
        """العودة للشاشة السابقة"""
        self.manager.current = 'home'
