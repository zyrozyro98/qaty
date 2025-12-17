# -*- coding: utf-8 -*-
"""
مسارات لوحة تحكم المدير
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.models import *
from app.database import db
from datetime import datetime, timedelta
import json
import random

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(f):
    """تحقق من أن المستخدم هو مدير"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """إحصائيات لوحة التحكم"""
    try:
        # إحصائيات المستخدمين
        total_users = User.query.count()
        total_sellers = User.query.filter_by(role='seller').count()
        total_buyers = User.query.filter_by(role='buyer').count()
        total_drivers = User.query.filter_by(role='driver').count()
        
        # إحصائيات المنتجات
        total_products = Product.query.count()
        available_products = Product.query.filter_by(is_available=True).count()
        
        # إحصائيات الطلبات
        total_orders = Order.query.count()
        today = datetime.utcnow().date()
        today_orders = Order.query.filter(
            db.func.date(Order.created_at) == today
        ).count()
        
        # إحصائيات المبيعات
        total_sales = db.session.query(db.func.sum(Order.final_price)).scalar() or 0
        today_sales = db.session.query(db.func.sum(Order.final_price)).filter(
            db.func.date(Order.created_at) == today
        ).scalar() or 0
        
        # إحصائيات المحفظة
        total_wallet_balance = db.session.query(db.func.sum(User.wallet_balance)).scalar() or 0
        
        # طلبات السحب
        pending_withdrawals = Withdrawal.query.filter_by(status='pending').count()
        
        return jsonify({
            'success': True,
            'stats': {
                'users': {
                    'total': total_users,
                    'sellers': total_sellers,
                    'buyers': total_buyers,
                    'drivers': total_drivers
                },
                'products': {
                    'total': total_products,
                    'available': available_products
                },
                'orders': {
                    'total': total_orders,
                    'today': today_orders,
                    'total_sales': float(total_sales),
                    'today_sales': float(today_sales)
                },
                'wallet': {
                    'total_balance': float(total_wallet_balance)
                },
                'withdrawals': {
                    'pending': pending_withdrawals
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في جلب الإحصائيات'}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """جلب جميع المستخدمين"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role')
        search = request.args.get('search')
        
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.ilike(f'%{search}%'),
                    User.full_name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.phone.ilike(f'%{search}%')
                )
            )
        
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'total': users.total,
                'pages': users.pages,
                'current_page': users.page,
                'per_page': users.per_page,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting users: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في جلب المستخدمين'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def manage_user(user_id):
    """إدارة مستخدم محدد"""
    try:
        user = User.query.get_or_404(user_id)
        
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'user': user.to_dict()
            })
            
        elif request.method == 'PUT':
            data = request.get_json()
            
            # تحديث البيانات
            if 'full_name' in data:
                user.full_name = data['full_name']
            if 'email' in data:
                user.email = data['email']
            if 'phone' in data:
                user.phone = data['phone']
            if 'role' in data:
                user.role = data['role']
            if 'store_name' in data:
                user.store_name = data['store_name']
            if 'vehicle_type' in data:
                user.vehicle_type = data['vehicle_type']
            if 'wallet_balance' in data:
                user.wallet_balance = float(data['wallet_balance'])
            if 'is_active' in data:
                user.is_active = bool(data['is_active'])
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم تحديث بيانات المستخدم',
                'user': user.to_dict()
            })
            
        elif request.method == 'DELETE':
            # لا يمكن حذف المستخدم إذا كان لديه طلبات
            has_orders = Order.query.filter(
                db.or_(Order.buyer_id == user_id, Order.seller_id == user_id)
            ).first()
            
            if has_orders:
                return jsonify({
                    'success': False,
                    'message': 'لا يمكن حذف مستخدم لديه طلبات'
                }), 400
            
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم حذف المستخدم بنجاح'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error managing user {user_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في إدارة المستخدم'}), 500

@admin_bp.route('/markets', methods=['GET', 'POST'])
@admin_required
def manage_markets():
    """إدارة الأسواق"""
    try:
        if request.method == 'GET':
            markets = Market.query.filter_by(is_active=True).all()
            return jsonify({
                'success': True,
                'markets': [market.to_dict() for market in markets]
            })
            
        elif request.method == 'POST':
            data = request.get_json()
            
            # التحقق من البيانات المطلوبة
            required_fields = ['name', 'location', 'city']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        'success': False,
                        'message': f'حقل {field} مطلوب'
                    }), 400
            
            # إنشاء السوق الجديد
            market = Market(
                name=data['name'],
                location=data['location'],
                city=data['city'],
                lat=data.get('lat'),
                lng=data.get('lng'),
                is_active=True
            )
            
            db.session.add(market)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم إنشاء السوق بنجاح',
                'market': market.to_dict()
            }), 201
            
    except Exception as e:
        current_app.logger.error(f"Error managing markets: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في إدارة الأسواق'}), 500

@admin_bp.route('/markets/<int:market_id>', methods=['PUT', 'DELETE'])
@admin_required
def manage_market(market_id):
    """إدارة سوق محدد"""
    try:
        market = Market.query.get_or_404(market_id)
        
        if request.method == 'PUT':
            data = request.get_json()
            
            if 'name' in data:
                market.name = data['name']
            if 'location' in data:
                market.location = data['location']
            if 'city' in data:
                market.city = data['city']
            if 'lat' in data:
                market.lat = data['lat']
            if 'lng' in data:
                market.lng = data['lng']
            if 'is_active' in data:
                market.is_active = bool(data['is_active'])
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم تحديث بيانات السوق',
                'market': market.to_dict()
            })
            
        elif request.method == 'DELETE':
            # لا يمكن حذف سوق إذا كان لديه منتجات أو مغاسل
            has_products = Product.query.filter_by(market_id=market_id).first()
            has_washers = QatWasher.query.filter_by(market_id=market_id).first()
            
            if has_products or has_washers:
                return jsonify({
                    'success': False,
                    'message': 'لا يمكن حذف سوق لديه منتجات أو مغاسل'
                }), 400
            
            db.session.delete(market)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم حذف السوق بنجاح'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error managing market {market_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في إدارة السوق'}), 500

@admin_bp.route('/washers', methods=['GET', 'POST'])
@admin_required
def manage_washers():
    """إدارة مغاسل القات"""
    try:
        if request.method == 'GET':
            market_id = request.args.get('market_id')
            
            query = QatWasher.query
            
            if market_id:
                query = query.filter_by(market_id=market_id)
            
            washers = query.all()
            
            return jsonify({
                'success': True,
                'washers': [washer.to_dict() for washer in washers]
            })
            
        elif request.method == 'POST':
            data = request.get_json()
            
            # التحقق من البيانات المطلوبة
            required_fields = ['market_id', 'name', 'phone']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        'success': False,
                        'message': f'حقل {field} مطلوب'
                    }), 400
            
            # التحقق من وجود السوق
            market = Market.query.get(data['market_id'])
            if not market:
                return jsonify({
                    'success': False,
                    'message': 'السوق غير موجود'
                }), 404
            
            # إنشاء المغسلة الجديدة
            washer = QatWasher(
                market_id=data['market_id'],
                name=data['name'],
                phone=data['phone'],
                owner_name=data.get('owner_name'),
                price_per_wash=data.get('price_per_wash', 100.0),
                is_available=True
            )
            
            db.session.add(washer)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم إنشاء مغسلة القات بنجاح',
                'washer': washer.to_dict()
            }), 201
            
    except Exception as e:
        current_app.logger.error(f"Error managing washers: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في إدارة المغاسل'}), 500

@admin_bp.route('/ad-packages', methods=['GET', 'POST'])
@admin_required
def manage_ad_packages():
    """إدارة باقات الإعلانات"""
    try:
        if request.method == 'GET':
            packages = AdPackage.query.filter_by(is_active=True).all()
            
            return jsonify({
                'success': True,
                'packages': [package.to_dict() for package in packages]
            })
            
        elif request.method == 'POST':
            data = request.get_json()
            
            # التحقق من البيانات المطلوبة
            required_fields = ['name', 'duration_days', 'price']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'message': f'حقل {field} مطلوب'
                    }), 400
            
            # إنشاء الباقة الجديدة
            package = AdPackage(
                name=data['name'],
                description=data.get('description'),
                duration_days=data['duration_days'],
                price=float(data['price']),
                max_impressions=data.get('max_impressions'),
                is_active=True
            )
            
            db.session.add(package)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم إنشاء باقة الإعلانات بنجاح',
                'package': package.to_dict()
            }), 201
            
    except Exception as e:
        current_app.logger.error(f"Error managing ad packages: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في إدارة باقات الإعلانات'}), 500

@admin_bp.route('/gift-codes', methods=['POST'])
@admin_required
def create_gift_codes():
    """إنشاء أكواد هدايا"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['amount', 'count']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'حقل {field} مطلوب'
                }), 400
        
        amount = float(data['amount'])
        count = int(data['count'])
        expires_days = data.get('expires_days', 30)
        
        if amount <= 0 or count <= 0:
            return jsonify({
                'success': False,
                'message': 'المبلغ والعدد يجب أن يكونا أكبر من الصفر'
            }), 400
        
        # إنشاء الأكواد
        codes = []
        for i in range(count):
            code = f"GIFT{random.randint(10000, 99999)}"
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
            
            gift_code = GiftCode(
                code=code,
                amount=amount,
                created_by=current_user_id,
                expires_at=expires_at,
                is_used=False
            )
            
            db.session.add(gift_code)
            codes.append(code)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'تم إنشاء {count} كود هدية',
            'codes': codes,
            'amount': amount,
            'expires_days': expires_days
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating gift codes: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في إنشاء أكواد الهدايا'}), 500

@admin_bp.route('/withdrawals', methods=['GET'])
@admin_required
def get_withdrawals():
    """جلب طلبات السحب"""
    try:
        status = request.args.get('status', 'pending')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Withdrawal.query
        
        if status:
            query = query.filter_by(status=status)
        
        withdrawals = query.order_by(Withdrawal.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # إضافة معلومات المستخدم
        withdrawals_data = []
        for withdrawal in withdrawals.items:
            withdrawal_dict = withdrawal.to_dict()
            user = User.query.get(withdrawal.user_id)
            if user:
                withdrawal_dict['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name
                }
            withdrawals_data.append(withdrawal_dict)
        
        return jsonify({
            'success': True,
            'withdrawals': withdrawals_data,
            'pagination': {
                'total': withdrawals.total,
                'pages': withdrawals.pages,
                'current_page': withdrawals.page,
                'per_page': withdrawals.per_page,
                'has_next': withdrawals.has_next,
                'has_prev': withdrawals.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting withdrawals: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في جلب طلبات السحب'}), 500

@admin_bp.route('/withdrawals/<int:withdrawal_id>/process', methods=['PUT'])
@admin_required
def process_withdrawal(withdrawal_id):
    """معالجة طلب سحب"""
    try:
        data = request.get_json()
        action = data.get('action')  # approve, reject
        notes = data.get('notes', '')
        
        if action not in ['approve', 'reject']:
            return jsonify({
                'success': False,
                'message': 'الإجراء غير صحيح'
            }), 400
        
        withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
        
        if withdrawal.status != 'pending':
            return jsonify({
                'success': False,
                'message': 'تم معالجة هذا الطلب مسبقاً'
            }), 400
        
        if action == 'approve':
            withdrawal.status = 'completed'
            withdrawal.processed_at = datetime.utcnow()
            withdrawal.admin_notes = notes
            
            # المبلغ تم خصمه مسبقاً عند إنشاء الطلب
            # لا حاجة لفعل أي شيء هنا
            
        elif action == 'reject':
            withdrawal.status = 'rejected'
            withdrawal.processed_at = datetime.utcnow()
            withdrawal.admin_notes = notes
            
            # إعادة المبلغ للمستخدم
            user = User.query.get(withdrawal.user_id)
            if user:
                user.wallet_balance += withdrawal.amount
        
        db.session.commit()
        
        # إرسال إشعار للمستخدم
        notification = Notification(
            user_id=withdrawal.user_id,
            type='withdrawal_processed',
            title='تحديث حالة طلب السحب',
            message=f'تم {("قبول" if action == "approve" else "رفض")} طلب سحبك بقيمة {withdrawal.amount} ريال',
            data={'withdrawal_id': withdrawal.id, 'status': withdrawal.status}
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'تم {action} طلب السحب بنجاح',
            'withdrawal': withdrawal.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error processing withdrawal {withdrawal_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في معالجة طلب السحب'}), 500

@admin_bp.route('/system/init', methods=['POST'])
@admin_required
def init_system():
    """تهيئة النظام ببيانات أولية"""
    try:
        current_user_id = get_jwt_identity()
        
        # 1. إنشاء أسواق افتراضية
        default_markets = [
            {
                'name': 'سوق تعز',
                'location': 'وسط المدينة',
                'city': 'تعز',
                'lat': 13.5789,
                'lng': 44.0219
            },
            {
                'name': 'سوق صنعاء',
                'location': 'شارع الزبيري',
                'city': 'صنعاء',
                'lat': 15.3694,
                'lng': 44.1910
            },
            {
                'name': 'سوق الحديدة',
                'location': 'الميناء',
                'city': 'الحديدة',
                'lat': 14.8022,
                'lng': 42.9545
            },
            {
                'name': 'سوق إب',
                'location': 'وسط المحافظة',
                'city': 'إب',
                'lat': 13.9667,
                'lng': 44.1833
            }
        ]
        
        for market_data in default_markets:
            market = Market.query.filter_by(name=market_data['name']).first()
            if not market:
                market = Market(**market_data)
                db.session.add(market)
        
        db.session.commit()
        
        # 2. إنشاء مغاسل افتراضية
        markets = Market.query.all()
        for market in markets:
            washer = QatWasher.query.filter_by(market_id=market.id).first()
            if not washer:
                washer = QatWasher(
                    market_id=market.id,
                    name=f'مغسلة {market.name}',
                    phone='771234567',
                    owner_name='مدير المغسلة',
                    price_per_wash=100.0,
                    is_available=True
                )
                db.session.add(washer)
        
        db.session.commit()
        
        # 3. إنشاء باقات إعلانات افتراضية
        default_packages = [
            {
                'name': 'الباقة الأساسية',
                'description': 'إعلان لمدة 7 أيام يظهر في التطبيق',
                'duration_days': 7,
                'price': 50.0,
                'max_impressions': 1000
            },
            {
                'name': 'الباقة المتوسطة',
                'description': 'إعلان مميز لمدة 30 يوماً',
                'duration_days': 30,
                'price': 200.0,
                'max_impressions': 5000
            },
            {
                'name': 'الباقة المميزة',
                'description': 'إعلان في الصفحة الرئيسية لمدة 60 يوماً',
                'duration_days': 60,
                'price': 500.0,
                'max_impressions': 15000
            }
        ]
        
        for package_data in default_packages:
            package = AdPackage.query.filter_by(name=package_data['name']).first()
            if not package:
                package = AdPackage(**package_data)
                db.session.add(package)
        
        db.session.commit()
        
        # 4. إنشاء مستخدمين تجريبيين (إذا لم يكن هناك مستخدمين)
        if User.query.count() <= 1:  # فقط المدير موجود
            demo_users = [
                {
                    'username': 'seller1',
                    'password': '123456',
                    'full_name': 'بائع تجريبي ١',
                    'email': 'seller1@qat.com',
                    'phone': '771000001',
                    'role': 'seller',
                    'store_name': 'متجر القات الأول'
                },
                {
                    'username': 'buyer1',
                    'password': '123456',
                    'full_name': 'مشتري تجريبي ١',
                    'email': 'buyer1@qat.com',
                    'phone': '771000002',
                    'role': 'buyer',
                    'wallet_balance': 1000.0
                },
                {
                    'username': 'driver1',
                    'password': '123456',
                    'full_name': 'مندوب توصيل ١',
                    'email': 'driver1@qat.com',
                    'phone': '771000003',
                    'role': 'driver',
                    'vehicle_type': 'دراجة نارية'
                }
            ]
            
            for user_data in demo_users:
                user = User(**user_data)
                db.session.add(user)
            
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تهيئة النظام ببيانات أولية',
            'data': {
                'markets_created': Market.query.count(),
                'washers_created': QatWasher.query.count(),
                'packages_created': AdPackage.query.count(),
                'users_created': User.query.count() - 1  # بدون المدير
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error initializing system: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في تهيئة النظام'}), 500
