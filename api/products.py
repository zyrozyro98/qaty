from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Product, Market, User, Review
from datetime import datetime

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    try:
        # الحصول على معاملات التصفية
        category = request.args.get('category')
        market_id = request.args.get('market_id')
        seller_id = request.args.get('seller_id')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        search = request.args.get('search')
        
        # بناء الاستعلام
        query = Product.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        if market_id:
            query = query.filter_by(market_id=market_id)
        if seller_id:
            query = query.filter_by(seller_id=seller_id)
        if min_price:
            query = query.filter(Product.price >= float(min_price))
        if max_price:
            query = query.filter(Product.price <= float(max_price))
        if search:
            query = query.filter(
                Product.name.ilike(f'%{search}%') | 
                Product.description.ilike(f'%{search}%')
            )
        
        # الحصول على النتائج
        products = query.order_by(Product.created_at.desc()).all()
        
        return jsonify({
            'products': [p.to_dict() for p in products],
            'count': len(products)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        
        if not product or not product.is_active:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        return jsonify({'product': product.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/add', methods=['POST'])
@jwt_required()
def add_product():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.user_type != 'seller':
            return jsonify({'error': 'غير مصرح لك بإضافة منتجات'}), 403
        
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'price']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'حقل {field} مطلوب'}), 400
        
        # إنشاء المنتج
        product = Product(
            name=data['name'],
            price=float(data['price']),
            seller_id=user_id,
            category=data.get('category'),
            description=data.get('description'),
            quantity=data.get('quantity', 0),
            image_url=data.get('image_url'),
            market_id=data.get('market_id')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة المنتج بنجاح',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>/update', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    try:
        user_id = get_jwt_identity()
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        # التحقق من صلاحية المستخدم
        if str(product.seller_id) != user_id:
            return jsonify({'error': 'غير مصرح لك بتعديل هذا المنتج'}), 403
        
        data = request.get_json()
        
        # تحديث البيانات
        if 'name' in data:
            product.name = data['name']
        if 'price' in data:
            product.price = float(data['price'])
        if 'category' in data:
            product.category = data['category']
        if 'description' in data:
            product.description = data['description']
        if 'quantity' in data:
            product.quantity = int(data['quantity'])
        if 'image_url' in data:
            product.image_url = data['image_url']
        if 'market_id' in data:
            product.market_id = data['market_id']
        if 'is_active' in data:
            product.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث المنتج',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    try:
        user_id = get_jwt_identity()
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        # التحقق من صلاحية المستخدم
        if str(product.seller_id) != user_id:
            return jsonify({'error': 'غير مصرح لك بحذف هذا المنتج'}), 403
        
        # حذف المنتج
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المنتج بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>/reviews', methods=['GET'])
def get_reviews(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        reviews = Review.query.filter_by(product_id=product_id, is_active=True).all()
        
        return jsonify({
            'reviews': [r.to_dict() for r in reviews],
            'count': len(reviews)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>/review', methods=['POST'])
@jwt_required()
def add_review(product_id):
    try:
        user_id = get_jwt_identity()
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        data = request.get_json()
        
        if 'rating' not in data or not (1 <= int(data['rating']) <= 5):
            return jsonify({'error': 'التقييم يجب أن يكون بين 1 و 5'}), 400
        
        # إنشاء التقييم
        review = Review(
            user_id=user_id,
            product_id=product_id,
            seller_id=product.seller_id,
            rating=int(data['rating']),
            comment=data.get('comment')
        )
        
        db.session.add(review)
        db.session.commit()
        
        # تحديث تقييم المنتج
        product_reviews = Review.query.filter_by(product_id=product_id, is_active=True).all()
        if product_reviews:
            product.rating = sum(r.rating for r in product_reviews) / len(product_reviews)
            product.total_ratings = len(product_reviews)
        
        # تحديث تقييم البائع
        seller_reviews = Review.query.filter_by(seller_id=product.seller_id, is_active=True).all()
        if seller_reviews:
            seller = User.query.get(product.seller_id)
            seller.rating = sum(r.rating for r in seller_reviews) / len(seller_reviews)
            seller.total_ratings = len(seller_reviews)
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة التقييم',
            'review': review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
