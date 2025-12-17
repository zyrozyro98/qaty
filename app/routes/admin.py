"""
مسارات المدير
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Product, Order, Market
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__)

def admin_required(f):
    """تحقق من أن المستخدم هو مدير"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        user = User.query.get(current_user['id'])
        
        if not user or user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك بالوصول'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    """جلب إحصائيات النظام"""
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
        today = datetime.now().date()
        today_orders = Order.query.filter(
            db.func.date(Order.created_at) == today
        ).count()
        
        # إحصائيات المبيعات
        total_sales = db.session.query(db.func.sum(Order.final_price)).scalar() or 0
        today_sales = db.session.query(db.func.sum(Order.final_price)).filter(
            db.func.date(Order.created_at) == today
        ).scalar() or 0
        
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
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في جلب الإحصائيات: {str(e)}'
        }), 500

@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """جلب جميع المستخدمين"""
    try:
        users = User.query.all()
        
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'wallet_balance': user.wallet_balance,
                'store_name': user.store_name,
                'vehicle_type': user.vehicle_type,
                'rating': user.rating,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({
            'success': True,
            'users': result,
            'count': len(result)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في جلب المستخدمين: {str(e)}'
        }), 500

@bp.route('/init-system', methods=['POST'])
@admin_required
def init_system():
    """تهيئة النظام ببيانات أولية"""
    try:
        current_user = get_jwt_identity()
        
        # إنشاء أسواق افتراضية
        markets = [
            Market(name='سوق تعز', location='وسط المدينة', city='تعز'),
            Market(name='سوق صنعاء', location='شارع الزبيري', city='صنعاء'),
            Market(name='سوق الحديدة', location='الميناء', city='الحديدة'),
            Market(name='سوق إب', location='وسط المحافظة', city='إب')
        ]
        
        for market in markets:
            if not Market.query.filter_by(name=market.name).first():
                db.session.add(market)
        
        # إنشاء مستخدمين تجريبيين
        demo_users = [
            User(
                username='seller1',
                password='123456',
                full_name='بائع تجريبي ١',
                email='seller1@qat-app.com',
                phone='771000001',
                role='seller',
                store_name='متجر القات الأول',
                wallet_balance=5000.0
            ),
            User(
                username='buyer1',
                password='123456',
                full_name='مشتري تجريبي ١',
                email='buyer1@qat-app.com',
                phone='771000002',
                role='buyer',
                wallet_balance=1000.0
            ),
            User(
                username='driver1',
                password='123456',
                full_name='مندوب توصيل ١',
                email='driver1@qat-app.com',
                phone='771000003',
                role='driver',
                vehicle_type='دراجة نارية',
                wallet_balance=500.0
            )
        ]
        
        for demo_user in demo_users:
            if not User.query.filter_by(username=demo_user.username).first():
                # تشفير كلمة المرور
                import hashlib
                demo_user.password = hashlib.sha256(demo_user.password.encode()).hexdigest()
                db.session.add(demo_user)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تهيئة النظام بنجاح',
            'data': {
                'markets_created': Market.query.count(),
                'users_created': User.query.count() - 1  # بدون المدير
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في تهيئة النظام: {str(e)}'
        }), 500
