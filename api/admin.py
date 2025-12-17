from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Product, Order, Market, WashingStation, Advertisement, AdPackage, Transaction
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def is_admin(user_id):
    """التحقق مما إذا كان المستخدم مديراً"""
    user = User.query.get(user_id)
    return user and user.user_type == 'admin'

@admin_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        # إحصائيات النظام
        stats = {
            'total_users': User.query.count(),
            'total_buyers': User.query.filter_by(user_type='buyer').count(),
            'total_sellers': User.query.filter_by(user_type='seller').count(),
            'total_drivers': User.query.filter_by(user_type='driver').count(),
            'total_products': Product.query.count(),
            'active_products': Product.query.filter_by(is_active=True).count(),
            'total_orders': Order.query.count(),
            'today_orders': Order.query.filter(
                Order.created_at >= datetime.now().date()
            ).count(),
            'total_revenue': db.session.query(db.func.sum(Order.total_price)).filter(
                Order.payment_status == 'paid'
            ).scalar() or 0,
            'pending_withdrawals': Transaction.query.filter_by(
                transaction_type='withdrawal',
                status='pending'
            ).count(),
            'active_markets': Market.query.filter_by(is_active=True).count(),
            'active_washing_stations': WashingStation.query.filter_by(is_active=True).count()
        }
        
        # إحصائيات الطلبات حسب الحالة
        order_statuses = ['pending', 'confirmed', 'washing', 'delivering', 'delivered', 'cancelled']
        orders_by_status = {}
        
        for status in order_statuses:
            orders_by_status[status] = Order.query.filter_by(status=status).count()
        
        stats['orders_by_status'] = orders_by_status
        
        # إحصائيات المبيعات اليومية للأسبوع الماضي
        daily_sales = []
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            total = db.session.query(db.func.sum(Order.total_price)).filter(
                db.func.date(Order.created_at) == date,
                Order.payment_status == 'paid'
            ).scalar() or 0
            
            daily_sales.append({
                'date': date.isoformat(),
                'total': float(total)
            })
        
        stats['daily_sales'] = list(reversed(daily_sales))
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        # الحصول على معاملات التصفية
        user_type = request.args.get('user_type')
        is_active = request.args.get('is_active')
        search = request.args.get('search')
        
        # بناء الاستعلام
        query = User.query
        
        if user_type:
            query = query.filter_by(user_type=user_type)
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        if search:
            query = query.filter(
                (User.name.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%')) |
                (User.phone.ilike(f'%{search}%'))
            )
        
        users = query.order_by(User.created_at.desc()).all()
        
        return jsonify({
            'users': [u.to_dict() for u in users],
            'count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/update', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        admin_id = get_jwt_identity()
        
        if not is_admin(admin_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'المستخدم غير موجود'}), 404
        
        data = request.get_json()
        
        # تحديث البيانات
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'user_type' in data:
            user.user_type = data['user_type']
        if 'store_name' in data and data['user_type'] == 'seller':
            user.store_name = data['store_name']
        if 'vehicle_type' in data and data['user_type'] == 'driver':
            user.vehicle_type = data['vehicle_type']
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث المستخدم',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/markets', methods=['GET'])
@jwt_required()
def get_markets():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        markets = Market.query.order_by(Market.created_at.desc()).all()
        
        return jsonify({
            'markets': [m.to_dict() for m in markets],
            'count': len(markets)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/markets/add', methods=['POST'])
@jwt_required()
def add_market():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({'error': 'اسم السوق مطلوب'}), 400
        
        market = Market(
            name=data['name'],
            location=data.get('location'),
            city=data.get('city'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(market)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة السوق',
            'market': market.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/washing-stations', methods=['GET'])
@jwt_required()
def get_washing_stations():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        stations = WashingStation.query.order_by(WashingStation.created_at.desc()).all()
        
        return jsonify({
            'stations': [s.to_dict() for s in stations],
            'count': len(stations)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/washing-stations/add', methods=['POST'])
@jwt_required()
def add_washing_station():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        data = request.get_json()
        
        required_fields = ['name', 'market_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'حقل {field} مطلوب'}), 400
        
        station = WashingStation(
            name=data['name'],
            market_id=data['market_id'],
            manager_id=data.get('manager_id'),
            phone=data.get('phone'),
            washing_price=data.get('washing_price', 100.0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(station)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة محطة الغسيل',
            'station': station.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/advertisements', methods=['GET'])
@jwt_required()
def get_advertisements():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        ads = Advertisement.query.order_by(Advertisement.created_at.desc()).all()
        
        return jsonify({
            'advertisements': [a.to_dict() for a in ads],
            'count': len(ads)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/advertisements/add', methods=['POST'])
@jwt_required()
def add_advertisement():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        data = request.get_json()
        
        required_fields = ['title', 'ad_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'حقل {field} مطلوب'}), 400
        
        ad = Advertisement(
            title=data['title'],
            description=data.get('description'),
            image_url=data.get('image_url'),
            target_url=data.get('target_url'),
            ad_type=data['ad_type'],
            position=data.get('position'),
            is_active=data.get('is_active', True),
            start_date=datetime.fromisoformat(data['start_date']) if 'start_date' in data else None,
            end_date=datetime.fromisoformat(data['end_date']) if 'end_date' in data else None
        )
        
        db.session.add(ad)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة الإعلان',
            'advertisement': ad.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/ad-packages', methods=['GET'])
@jwt_required()
def get_ad_packages():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        packages = AdPackage.query.filter_by(is_active=True).all()
        
        return jsonify({
            'packages': [p.to_dict() for p in packages],
            'count': len(packages)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/ad-packages/add', methods=['POST'])
@jwt_required()
def add_ad_package():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        data = request.get_json()
        
        required_fields = ['name', 'price', 'duration_days']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'حقل {field} مطلوب'}), 400
        
        package = AdPackage(
            name=data['name'],
            description=data.get('description'),
            price=float(data['price']),
            duration_days=int(data['duration_days']),
            max_impressions=data.get('max_impressions'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(package)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة الباقة الإعلانية',
            'package': package.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/transactions/pending', methods=['GET'])
@jwt_required()
def get_pending_transactions():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        # الحصول على طلبات السحب المعلقة
        transactions = Transaction.query.filter_by(
            transaction_type='withdrawal',
            status='pending'
        ).order_by(Transaction.created_at.desc()).all()
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions],
            'count': len(transactions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/transactions/<int:transaction_id>/approve', methods=['POST'])
@jwt_required()
def approve_transaction(transaction_id):
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({'error': 'المعاملة غير موجودة'}), 404
        
        if transaction.status != 'pending':
            return jsonify({'error': 'المعاملة ليست معلقة'}), 400
        
        # الموافقة على المعاملة
        transaction.status = 'completed'
        transaction.notes = transaction.notes + ' - تمت الموافقة'
        
        db.session.commit()
        
        return jsonify({
            'message': 'تمت الموافقة على المعاملة',
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/gift-codes/generate', methods=['POST'])
@jwt_required()
def generate_gift_codes():
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'غير مصرح'}), 403
        
        data = request.get_json()
        
        required_fields = ['amount', 'count', 'expiry_days']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'حقل {field} مطلوب'}), 400
        
        amount = float(data['amount'])
        count = int(data['count'])
        expiry_days = int(data['expiry_days'])
        
        # هنا يمكن إنشاء أكواد الهدايا وتخزينها في قاعدة بيانات
        # هذا مثال مبسط
        
        codes = []
        import random
        import string
        
        for i in range(count):
            code = 'GIFT' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            codes.append({
                'code': code,
                'amount': amount,
                'expiry_date': (datetime.now() + timedelta(days=expiry_days)).isoformat()
            })
        
        return jsonify({
            'message': f'تم إنشاء {count} كود هدية',
            'codes': codes
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
