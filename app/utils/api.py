# -*- coding: utf-8 -*-
"""
واجهة برمجة التطبيقات (API) للتواصل مع السيرفر
"""
import json
import ssl
from urllib.request import Request, urlopen
from urllib.error import URLError
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

class API:
    """فئة API للتواصل مع السيرفر"""
    
    BASE_URL = "https://your-server.com/api"  # تغيير هذا لعنوان السيرفر الحقيقي
    LOCAL_URL = "http://localhost:5000/api"  # للاختبار المحلي
    
    def __init__(self):
        self.is_online_mode = True  # True للاتصال بالسيرفر، False للوضع المحلي
    
    def is_online(self):
        """فحص إذا كان التطبيق متصل بالانترنت"""
        # في التطبيق الحقيقي، هنا نفحص الاتصال بالانترنت
        return self.is_online_mode
    
    def login(self, username, password, success_callback, error_callback):
        """تسجيل الدخول"""
        data = {
            'username': username,
            'password': password
        }
        
        if self.is_online():
            self._make_request(
                '/auth/login',
                data,
                success_callback,
                error_callback
            )
        else:
            # محاكاة API للاختبار
            Clock.schedule_once(lambda dt: self._mock_login(username, password, success_callback), 1)
    
    def register(self, user_data, success_callback, error_callback):
        """تسجيل مستخدم جديد"""
        if self.is_online():
            self._make_request(
                '/auth/register',
                user_data,
                success_callback,
                error_callback
            )
        else:
            # محاكاة API للاختبار
            Clock.schedule_once(lambda dt: self._mock_register(user_data, success_callback), 1)
    
    def get_products(self, filters=None, success_callback=None, error_callback=None):
        """جلب المنتجات"""
        if self.is_online():
            self._make_request(
                '/products',
                filters or {},
                success_callback,
                error_callback,
                method='GET'
            )
        else:
            # محاكاة API للاختبار
            Clock.schedule_once(lambda dt: self._mock_get_products(success_callback), 1)
    
    def create_order(self, order_data, token, success_callback, error_callback):
        """إنشاء طلب جديد"""
        if self.is_online():
            headers = {'Authorization': f'Bearer {token}'}
            self._make_request(
                '/orders/create',
                order_data,
                success_callback,
                error_callback,
                headers=headers
            )
        else:
            # محاكاة API للاختبار
            Clock.schedule_once(lambda dt: self._mock_create_order(order_data, success_callback), 1)
    
    def get_notifications(self, token, success_callback, error_callback):
        """جلب الإشعارات"""
        if self.is_online():
            headers = {'Authorization': f'Bearer {token}'}
            self._make_request(
                '/notifications',
                {},
                success_callback,
                error_callback,
                method='GET',
                headers=headers
            )
        else:
            # محاكاة API للاختبار
            Clock.schedule_once(lambda dt: self._mock_get_notifications(success_callback), 1)
    
    def _make_request(self, endpoint, data, success_callback, error_callback, 
                     method='POST', headers=None):
        """إنشاء طلب HTTP"""
        url = f"{self.BASE_URL}{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        try:
            req = UrlRequest(
                url,
                on_success=lambda req, result: success_callback(result),
                on_error=lambda req, error: error_callback(error),
                on_failure=lambda req, result: error_callback(result),
                req_body=json.dumps(data),
                req_headers=headers,
                timeout=30
            )
        except Exception as e:
            error_callback(str(e))
    
    # دوال المحاكاة للاختبار
    def _mock_login(self, username, password, callback):
        """محاكاة تسجيل الدخول"""
        test_users = {
            'admin': {'id': 1, 'role': 'admin', 'name': 'المدير العام'},
            'seller': {'id': 2, 'role': 'seller', 'name': 'بائع تجريبي'},
            'buyer': {'id': 3, 'role': 'buyer', 'name': 'مشتري تجريبي'},
            'driver': {'id': 4, 'role': 'driver', 'name': 'مندوب توصيل'}
        }
        
        if username in test_users and password == '123456':
            user_data = test_users[username]
            user_data.update({
                'username': username,
                'email': f'{username}@example.com',
                'phone': '771234567',
                'wallet_balance': 1000.0,
                'store_name': 'متجر تجريبي' if username == 'seller' else None,
                'vehicle_type': 'دراجة نارية' if username == 'driver' else None
            })
            
            response = {
                'success': True,
                'message': 'تم تسجيل الدخول بنجاح',
                'user': user_data,
                'token': 'mock-jwt-token-123'
            }
        else:
            response = {
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }
        
        callback(response)
    
    def _mock_register(self, user_data, callback):
        """محاكاة التسجيل"""
        response = {
            'success': True,
            'message': 'تم إنشاء الحساب بنجاح',
            'user_id': 999
        }
        callback(response)
    
    def _mock_get_products(self, callback):
        """محاكاة جلب المنتجات"""
        products = [
            {
                'id': 1,
                'name': 'قات صعدي ممتاز',
                'description': 'أجود أنواع القات الصعدي من أفضل المزارع',
                'price': 60.0,
                'category': 'صعدي',
                'quantity': 50,
                'seller_id': 2,
                'store_name': 'مزرعة الصعدي',
                'seller_rating': 4.8,
                'image_url': 'https://via.placeholder.com/300x200/4CAF50/FFFFFF?text=قات+صعدي'
            },
            {
                'id': 2,
                'name': 'قات همداني فاخر',
                'description': 'قات همداني طازج بنكهة مميزة',
                'price': 55.0,
                'category': 'همداني',
                'quantity': 30,
                'seller_id': 2,
                'store_name': 'محل الهمداني',
                'seller_rating': 4.6,
                'image_url': 'https://via.placeholder.com/300x200/2196F3/FFFFFF?text=قات+همداني'
            },
            {
                'id': 3,
                'name': 'قات أرحبي طازج',
                'description': 'قات أرحبي طازج من مزارع أرحب',
                'price': 45.0,
                'category': 'أرحبي',
                'quantity': 40,
                'seller_id': 2,
                'store_name': 'مزرعة أرحب',
                'seller_rating': 4.4,
                'image_url': 'https://via.placeholder.com/300x200/FF9800/FFFFFF?text=قات+أرحبي'
            }
        ]
        
        response = {
            'success': True,
            'products': products
        }
        callback(response)
    
    def _mock_create_order(self, order_data, callback):
        """محاكاة إنشاء طلب"""
        response = {
            'success': True,
            'message': 'تم إنشاء الطلب بنجاح',
            'order': {
                'id': 1001,
                'order_code': f"ORD{len(str(order_data))}",
                'total_price': order_data.get('quantity', 1) * 60.0,
                'washing_price': 100.0 if order_data.get('washing_required') else 0,
                'final_price': (order_data.get('quantity', 1) * 60.0) + (100.0 if order_data.get('washing_required') else 0),
                'status': 'confirmed',
                'estimated_delivery': '2024-01-20 14:30'
            }
        }
        callback(response)
    
    def _mock_get_notifications(self, callback):
        """محاكاة جلب الإشعارات"""
        notifications = [
            {
                'id': 1,
                'title': 'طلب جديد',
                'message': 'لديك طلب جديد #1001',
                'type': 'order_placed',
                'is_read': False,
                'created_at': '2024-01-20 10:30'
            },
            {
                'id': 2,
                'title': 'تم الشحن',
                'message': 'تم شحن 500 ريال لحسابك',
                'type': 'payment_received',
                'is_read': True,
                'created_at': '2024-01-19 15:45'
            },
            {
                'id': 3,
                'title': 'تقييم جديد',
                'message': 'تلقيت تقييماً جديداً على منتجك',
                'type': 'rating_added',
                'is_read': False,
                'created_at': '2024-01-18 09:20'
            }
        ]
        
        response = {
            'success': True,
            'notifications': notifications
        }
        callback(response)
