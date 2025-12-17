# -*- coding: utf-8 -*-
"""
واجهة API الحقيقية مع السيرفر
"""
import json
import hashlib
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
from app.utils.arabic_support import ArabicSupport

class RealAPI:
    """فئة API للتواصل مع السيرفر الحقيقي"""
    
    BASE_URL = "https://qaty.onrender.com"  #  هذا عنوان السيرفر الحقيقي
    API_KEY = "rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj"
    
    def __init__(self):
        self.token = None
        self.user_data = None
    
    def set_token(self, token):
        """تعيين token المصادقة"""
        self.token = token
    
    def set_user_data(self, user_data):
        """تعيين بيانات المستخدم"""
        self.user_data = user_data
    
    def make_request(self, endpoint, data, success_callback, error_callback, 
                     method='POST', headers=None):
        """إنشاء طلب HTTP"""
        url = f"{self.BASE_URL}{endpoint}"
        
        if headers is None:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}' if self.token else '',
                'X-API-Key': self.API_KEY
            }
        
        try:
            req = UrlRequest(
                url,
                on_success=lambda req, result: self._handle_success(result, success_callback),
                on_error=lambda req, error: self._handle_error(error, error_callback),
                on_failure=lambda req, result: self._handle_error(result, error_callback),
                req_body=json.dumps(data) if data and method != 'GET' else None,
                req_headers=headers,
                timeout=30,
                method=method
            )
        except Exception as e:
            error_callback(str(e))
    
    def _handle_success(self, result, callback):
        """معالجة النجاح"""
        try:
            # تحقق من أن النتيجة هي JSON
            if isinstance(result, dict):
                callback(result)
            else:
                callback({'success': False, 'message': 'استجابة غير صالحة'})
        except Exception as e:
            callback({'success': False, 'message': f'خطأ في معالجة الاستجابة: {str(e)}'})
    
    def _handle_error(self, error, callback):
        """معالجة الخطأ"""
        error_msg = str(error)
        if 'timed out' in error_msg:
            callback({'success': False, 'message': 'انتهت مهلة الاتصال'})
        elif 'Connection refused' in error_msg:
            callback({'success': False, 'message': 'تعذر الاتصال بالسيرفر'})
        else:
            callback({'success': False, 'message': f'خطأ في الاتصال: {error_msg}'})
    
    def login(self, username, password, success_callback, error_callback):
        """تسجيل الدخول"""
        data = {
            'username': username,
            'password': password
        }
        
        self.make_request(
            '/api/auth/login',
            data,
            success_callback,
            error_callback
        )
    
    def register(self, user_data, success_callback, error_callback):
        """تسجيل مستخدم جديد"""
        self.make_request(
            '/api/auth/register',
            user_data,
            success_callback,
            error_callback
        )
    
    def get_products(self, filters=None, success_callback=None, error_callback=None):
        """جلب المنتجات"""
        params = ''
        if filters:
            params = '?' + '&'.join([f'{k}={v}' for k, v in filters.items()])
        
        self.make_request(
            f'/api/products{params}',
            None,
            success_callback,
            error_callback,
            method='GET'
        )
    
    def create_order(self, order_data, success_callback, error_callback):
        """إنشاء طلب جديد"""
        self.make_request(
            '/api/orders/create',
            order_data,
            success_callback,
            error_callback
        )
    
    def get_notifications(self, success_callback, error_callback):
        """جلب الإشعارات"""
        self.make_request(
            '/api/notifications',
            None,
            success_callback,
            error_callback,
            method='GET'
        )
    
    def get_dashboard_stats(self, success_callback, error_callback):
        """جلب إحصائيات لوحة التحكم"""
        self.make_request(
            '/api/admin/dashboard/stats',
            None,
            success_callback,
            error_callback,
            method='GET'
        )
    
    def get_users(self, page=1, per_page=20, search=None, role=None, 
                  success_callback=None, error_callback=None):
        """جلب المستخدمين"""
        params = f'?page={page}&per_page={per_page}'
        if search:
            params += f'&search={search}'
        if role:
            params += f'&role={role}'
        
        self.make_request(
            f'/api/admin/users{params}',
            None,
            success_callback,
            error_callback,
            method='GET'
        )
    
    def create_user(self, user_data, success_callback, error_callback):
        """إنشاء مستخدم جديد (للمدير)"""
        self.make_request(
            '/api/admin/users',
            user_data,
            success_callback,
            error_callback,
            method='POST'
        )
    
    def delete_user(self, user_id, success_callback, error_callback):
        """حذف مستخدم"""
        self.make_request(
            f'/api/admin/users/{user_id}',
            None,
            success_callback,
            error_callback,
            method='DELETE'
        )
    
    def init_system(self, success_callback, error_callback):
        """تهيئة النظام"""
        self.make_request(
            '/api/admin/system/init',
            None,
            success_callback,
            error_callback,
            method='POST'
        )
    
    def create_gift_codes(self, amount, count, expires_days, success_callback, error_callback):
        """إنشاء أكواد هدايا"""
        data = {
            'amount': amount,
            'count': count,
            'expires_days': expires_days
        }
        
        self.make_request(
            '/api/admin/gift-codes',
            data,
            success_callback,
            error_callback,
            method='POST'
        )

# استخدام API الحقيقي بدلاً من المحاكاة
API = RealAPI()
