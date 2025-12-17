from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Order, Product, User, Wallet, Transaction, WashingStation, Market
from datetime import datetime, timedelta
import random
import string

orders_bp = Blueprint('orders', __name__)

def generate_order_code():
    """إنشاء رمز طلب فريد"""
    timestamp = datetime.now().strftime('%y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD{timestamp}{random_str}"

@orders_bp.route('/create', methods=['POST'])
@jwt_required()
def create_order():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['product_id', 'quantity']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'حقل {field} مطلوب'}), 400
        
        # الحصول على المنتج
        product = Product.query.get(data['product_id'])
        if not product or not product.is_active:
            return jsonify({'error': 'المنتج غير متوفر'}), 404
        
        # التحقق من الكمية
        if product.quantity < int(data['quantity']):
            return jsonify({'error': 'الكمية غير متوفرة'}), 400
        
        # حساب السعر
        unit_price = product.price
        washing_price = 0
        requires_washing = data.get('requires_washing', False)
        
        if requires_washing:
            # الحصول على سعر الغسيل من محطة الغسيل في السوق
            washing_station = WashingStation.query.filter_by(
                market_id=product.market_id,
                is_active=True
            ).first()
            
            if washing_station:
                washing_price = washing_station.washing_price
            else:
                washing_price = 100  # سعر افتراضي
        
        total_price = (unit_price * int(data['quantity'])) + washing_price
        
        # إنشاء رمز البيع
        sale_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # إنشاء الطلب
        order = Order(
            order_code=generate_order_code(),
            buyer_id=user_id,
            seller_id=product.seller_id,
            product_id=product.id,
            quantity=int(data['quantity']),
            unit_price=unit_price,
            washing_price=washing_price,
            total_price=total_price,
            requires_washing=requires_washing,
            sale_code=sale_code,
            delivery_address=data.get('delivery_address'),
            payment_method=data.get('payment_method', 'wallet'),
            payment_status='pending',
            status='pending'
        )
        
        db.session.add(order)
        db.session.commit()
        
        # تخفيض كمية المنتج
        product.quantity -= int(data['quantity'])
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء الطلب بنجاح',
            'order': order.to_dict(),
            'sale_code': sale_code
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/confirm/<int:order_id>', methods=['POST'])
@jwt_required()
def confirm_order(order_id):
    try:
        user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'الطلب غير موجود'}), 404
        
        # التحقق من صلاحية المستخدم (يجب أن يكون المشتري)
        if str(order.buyer_id) != user_id:
            return jsonify({'error': 'غير مصرح لك بتأكيد هذا الطلب'}), 403
        
        # التحقق من حالة الطلب
        if order.status != 'pending':
            return jsonify({'error': 'لا يمكن تأكيد هذا الطلب'}), 400
        
        # الحصول على محفظة المشتري
        buyer_wallet = Wallet.query.filter_by(user_id=order.buyer_id).first()
        if not buyer_wallet:
            return jsonify({'error': 'المحفظة غير موجودة'}), 404
        
        # التحقق من الرصيد
        if buyer_wallet.balance < order.total_price:
            return jsonify({'error': 'رصيد غير كافي'}), 400
        
        # خصم المبلغ من المشتري
        buyer_wallet.balance -= order.total_price
        
        # إضافة المبلغ للبائع
        seller_wallet = Wallet.query.filter_by(user_id=order.seller_id).first()
        if seller_wallet:
            seller_wallet.balance += order.total_price
        
        # تحديث حالة الطلب
        order.status = 'confirmed'
        order.payment_status = 'paid'
        order.payment_method = 'wallet'
        
        # إضافة معاملة الدفع
        transaction = Transaction(
            user_id=order.buyer_id,
            amount=-order.total_price,
            transaction_type='purchase',
            payment_method='wallet',
            status='completed',
            reference_number=f"PAY{order.id}{datetime.now().strftime('%Y%m%d')}",
            order_id=order.id,
            notes=f'شراء منتج #{order.product_id}'
        )
        db.session.add(transaction)
        
        # إضافة معاملة للبائع
        if seller_wallet:
            seller_transaction = Transaction(
                user_id=order.seller_id,
                amount=order.total_price,
                transaction_type='sale',
                payment_method='wallet',
                status='completed',
                reference_number=f"SALE{order.id}{datetime.now().strftime('%Y%m%d')}",
                order_id=order.id,
                notes=f'بيع منتج #{order.product_id}'
            )
            db.session.add(seller_transaction)
        
        # إذا كان يحتاج غسيل، إرسال إشعار لمحطة الغسيل
        if order.requires_washing and order.product.market_id:
            washing_station = WashingStation.query.filter_by(
                market_id=order.product.market_id,
                is_active=True
            ).first()
            
            if washing_station:
                order.washing_station_id = washing_station.id
                order.status = 'washing'
                
                # هنا يمكن إرسال إشعار عبر WebSocket
        
        # إرسال إشعار للبائع
        # هنا يمكن إرسال إشعار عبر WebSocket
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تأكيد الطلب بنجاح',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'المستخدم غير موجود'}), 404
        
        # الحصول على الطلبات حسب نوع المستخدم
        if user.user_type == 'buyer':
            orders = Order.query.filter_by(buyer_id=user_id).order_by(Order.created_at.desc()).all()
        elif user.user_type == 'seller':
            orders = Order.query.filter_by(seller_id=user_id).order_by(Order.created_at.desc()).all()
        elif user.user_type == 'driver':
            orders = Order.query.filter_by(driver_id=user_id).order_by(Order.created_at.desc()).all()
        else:
            orders = []
        
        return jsonify({
            'orders': [o.to_dict() for o in orders],
            'count': len(orders)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    try:
        user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'الطلب غير موجود'}), 404
        
        # التحقق من صلاحية المشاهدة
        user = User.query.get(user_id)
        if (str(order.buyer_id) != user_id and 
            str(order.seller_id) != user_id and 
            str(order.driver_id) != user_id and
            user.user_type != 'admin'):
            return jsonify({'error': 'غير مصرح لك بمشاهدة هذا الطلب'}), 403
        
        return jsonify({'order': order.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/assign-driver', methods=['POST'])
@jwt_required()
def assign_driver(order_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # التحقق من صلاحية المستخدم (مدير أو مشرف)
        if user.user_type not in ['admin', 'washing_manager']:
            return jsonify({'error': 'غير مصرح لك بتعيين سائق'}), 403
        
        data = request.get_json()
        if 'driver_id' not in data:
            return jsonify({'error': 'معرف السائق مطلوب'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'الطلب غير موجود'}), 404
        
        # التحقق من حالة الطلب
        if order.status not in ['confirmed', 'washing']:
            return jsonify({'error': 'لا يمكن تعيين سائق لهذا الطلب'}), 400
        
        # تعيين السائق
        driver = User.query.get(data['driver_id'])
        if not driver or driver.user_type != 'driver':
            return jsonify({'error': 'السائق غير موجود'}), 404
        
        order.driver_id = driver.id
        order.status = 'delivering'
        order.estimated_delivery = datetime.now() + timedelta(hours=1)
        
        db.session.commit()
        
        # إرسال إشعار للسائق
        # هنا يمكن إرسال إشعار عبر WebSocket
        
        return jsonify({
            'message': 'تم تعيين السائق بنجاح',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/deliver', methods=['POST'])
@jwt_required()
def deliver_order(order_id):
    try:
        user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'الطلب غير موجود'}), 404
        
        # التحقق من صلاحية المستخدم (يجب أن يكون السائق المعين)
        if str(order.driver_id) != user_id:
            return jsonify({'error': 'غير مصرح لك بتسليم هذا الطلب'}), 403
        
        # تحديث حالة الطلب
        order.status = 'delivered'
        order.delivered_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تسليم الطلب بنجاح',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
