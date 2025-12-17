"""
مسارات الطلبات
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from __init__ import db
from models import Order, Product, User
import random
from datetime import datetime, timedelta

bp = Blueprint('orders', __name__)

def generate_order_code():
    """توليد كود طلب فريد"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = random.randint(1000, 9999)
    return f'ORD{timestamp}{random_part}'

@bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    """إنشاء طلب جديد"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['product_id', 'quantity', 'delivery_address', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'حقل {field} مطلوب'
                }), 400
        
        # التحقق من المنتج
        product = Product.query.get(data['product_id'])
        if not product or not product.is_available:
            return jsonify({
                'success': False,
                'message': 'المنتج غير متوفر'
            }), 400
        
        if product.quantity < data['quantity']:
            return jsonify({
                'success': False,
                'message': 'الكمية غير متوفرة'
            }), 400
        
        # حساب الأسعار
        washing_required = data.get('washing_required', False)
        washing_price = 100.0 if washing_required else 0.0
        total_price = product.price * data['quantity']
        final_price = total_price + washing_price
        
        # توليد كود الطلب
        order_code = generate_order_code()
        
        # إنشاء الطلب
        order = Order(
            order_code=order_code,
            buyer_id=current_user['id'],
            seller_id=product.seller_id,
            product_id=product.id,
            quantity=data['quantity'],
            total_price=total_price,
            washing_price=washing_price,
            final_price=final_price,
            washing_required=washing_required,
            status='pending',
            payment_method=data['payment_method'],
            payment_status='pending',
            delivery_address=data['delivery_address'],
            delivery_notes=data.get('delivery_notes', ''),
            estimated_delivery=datetime.now() + timedelta(hours=1)
        )
        
        # تحديث كمية المنتج
        product.quantity -= data['quantity']
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء الطلب بنجاح',
            'order': {
                'id': order.id,
                'order_code': order.order_code,
                'total_price': order.total_price,
                'washing_price': order.washing_price,
                'final_price': order.final_price,
                'status': order.status,
                'estimated_delivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في إنشاء الطلب: {str(e)}'
        }), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """جلب طلبات المستخدم"""
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user['id'])
        
        if user.role == 'buyer':
            orders = Order.query.filter_by(buyer_id=user.id).all()
        elif user.role == 'seller':
            orders = Order.query.filter_by(seller_id=user.id).all()
        else:
            orders = []
        
        result = []
        for order in orders:
            result.append({
                'id': order.id,
                'order_code': order.order_code,
                'product_name': order.product.name if order.product else '',
                'quantity': order.quantity,
                'total_price': order.total_price,
                'washing_price': order.washing_price,
                'final_price': order.final_price,
                'washing_required': order.washing_required,
                'status': order.status,
                'payment_method': order.payment_method,
                'payment_status': order.payment_status,
                'delivery_address': order.delivery_address,
                'estimated_delivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None,
                'actual_delivery': order.actual_delivery.isoformat() if order.actual_delivery else None,
                'created_at': order.created_at.isoformat() if order.created_at else None
            })
        
        return jsonify({
            'success': True,
            'orders': result,
            'count': len(result)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في جلب الطلبات: {str(e)}'
        }), 500

@bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """جلب طلب محدد"""
    try:
        current_user = get_jwt_identity()
        order = Order.query.get_or_404(order_id)
        
        # التحقق من الصلاحيات
        user = User.query.get(current_user['id'])
        if user.role != 'admin' and order.buyer_id != user.id and order.seller_id != user.id:
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك بمشاهدة هذا الطلب'
            }), 403
        
        return jsonify({
            'success': True,
            'order': {
                'id': order.id,
                'order_code': order.order_code,
                'buyer_id': order.buyer_id,
                'seller_id': order.seller_id,
                'product_id': order.product_id,
                'product_name': order.product.name if order.product else '',
                'quantity': order.quantity,
                'total_price': order.total_price,
                'washing_price': order.washing_price,
                'final_price': order.final_price,
                'washing_required': order.washing_required,
                'status': order.status,
                'payment_method': order.payment_method,
                'payment_status': order.payment_status,
                'delivery_address': order.delivery_address,
                'delivery_notes': order.delivery_notes,
                'estimated_delivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None,
                'actual_delivery': order.actual_delivery.isoformat() if order.actual_delivery else None,
                'created_at': order.created_at.isoformat() if order.created_at else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في جلب الطلب: {str(e)}'
        }), 500
