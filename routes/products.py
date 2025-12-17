"""
مسارات المنتجات
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from __init__ import db
from models import Product, User

bp = Blueprint('products', __name__)

@bp.route('/', methods=['GET'])
def get_products():
    """جلب جميع المنتجات"""
    try:
        products = Product.query.filter_by(is_available=True).all()
        
        result = []
        for product in products:
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'category': product.category,
                'price': product.price,
                'quantity': product.quantity,
                'image_url': product.image_url,
                'rating': product.rating,
                'total_reviews': product.total_reviews,
                'seller_id': product.seller_id,
                'seller_name': product.seller.full_name if product.seller else '',
                'seller_store': product.seller.store_name if product.seller else '',
                'seller_rating': product.seller.rating if product.seller else 5.0,
                'created_at': product.created_at.isoformat() if product.created_at else None
            })
        
        return jsonify({
            'success': True,
            'products': result,
            'count': len(result)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في جلب المنتجات: {str(e)}'
        }), 500

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """جلب منتج محدد"""
    try:
        product = Product.query.get_or_404(product_id)
        
        return jsonify({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'category': product.category,
                'price': product.price,
                'quantity': product.quantity,
                'image_url': product.image_url,
                'rating': product.rating,
                'total_reviews': product.total_reviews,
                'seller_id': product.seller_id,
                'seller_name': product.seller.full_name if product.seller else '',
                'seller_store': product.seller.store_name if product.seller else '',
                'seller_rating': product.seller.rating if product.seller else 5.0,
                'created_at': product.created_at.isoformat() if product.created_at else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في جلب المنتج: {str(e)}'
        }), 404

@bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """إنشاء منتج جديد"""
    try:
        current_user = get_jwt_identity()
        
        # التحقق من أن المستخدم بائع
        user = User.query.get(current_user['id'])
        if not user or user.role != 'seller':
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك بإنشاء منتجات'
            }), 403
        
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'category', 'price', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'حقل {field} مطلوب'
                }), 400
        
        # إنشاء المنتج
        product = Product(
            seller_id=user.id,
            name=data['name'],
            description=data.get('description', ''),
            category=data['category'],
            price=float(data['price']),
            quantity=int(data['quantity']),
            image_url=data.get('image_url', ''),
            is_available=True
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء المنتج بنجاح',
            'product': {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في إنشاء المنتج: {str(e)}'
        }), 500

@bp.route('/seller', methods=['GET'])
@jwt_required()
def get_seller_products():
    """جلب منتجات البائع"""
    try:
        current_user = get_jwt_identity()
        
        products = Product.query.filter_by(seller_id=current_user['id']).all()
        
        result = []
        for product in products:
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'category': product.category,
                'price': product.price,
                'quantity': product.quantity,
                'image_url': product.image_url,
                'rating': product.rating,
                'total_reviews': product.total_reviews,
                'is_available': product.is_available,
                'created_at': product.created_at.isoformat() if product.created_at else None
            })
        
        return jsonify({
            'success': True,
            'products': result,
            'count': len(result)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في جلب منتجات البائع: {str(e)}'
        }), 500
