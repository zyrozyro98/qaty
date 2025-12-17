from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database import db
from models import User, Wallet
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # التحقق من البيانات
        required_fields = ['name', 'phone', 'email', 'password', 'user_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'حقل {field} مطلوب'}), 400
        
        # التحقق من صحة البريد الإلكتروني
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            return jsonify({'error': 'البريد الإلكتروني غير صالح'}), 400
        
        # التحقق من صحة رقم الهاتف (رقم يمني)
        if not re.match(r'^77[0-9]{7}$', data['phone']):
            return jsonify({'error': 'رقم الهاتف يجب أن يكون 10 أرقام ويبدأ بـ 77'}), 400
        
        # التحقق من وجود المستخدم
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'البريد الإلكتروني مسجل مسبقاً'}), 400
        
        if User.query.filter_by(phone=data['phone']).first():
            return jsonify({'error': 'رقم الهاتف مسجل مسبقاً'}), 400
        
        # إنشاء المستخدم
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            user_type=data['user_type']
        )
        user.set_password(data['password'])
        
        # إضافة معلومات إضافية حسب نوع المستخدم
        if data['user_type'] == 'seller' and 'store_name' in data:
            user.store_name = data['store_name']
        elif data['user_type'] == 'driver' and 'vehicle_type' in data:
            user.vehicle_type = data['vehicle_type']
        
        db.session.add(user)
        db.session.commit()
        
        # إنشاء محفظة للمستخدم
        wallet = Wallet(user_id=user.id)
        db.session.add(wallet)
        db.session.commit()
        
        # إنشاء توكن
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'تم إنشاء الحساب بنجاح',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'البريد الإلكتروني وكلمة المرور مطلوبان'}), 400
        
        # البحث بالمستخدم
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({'error': 'المستخدم غير موجود'}), 404
        
        # التحقق من كلمة المرور
        if not user.check_password(data['password']):
            return jsonify({'error': 'كلمة المرور غير صحيحة'}), 401
        
        # التحقق من حالة الحساب
        if not user.is_active:
            return jsonify({'error': 'الحساب غير مفعل'}), 403
        
        # إنشاء توكن
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'تم تسجيل الدخول بنجاح',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'المستخدم غير موجود'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile/update', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'المستخدم غير موجود'}), 404
        
        data = request.get_json()
        
        # تحديث البيانات المسموح بها
        if 'name' in data:
            user.name = data['name']
        if 'store_name' in data and user.user_type == 'seller':
            user.store_name = data['store_name']
        if 'vehicle_type' in data and user.user_type == 'driver':
            user.vehicle_type = data['vehicle_type']
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الملف الشخصي',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/wallet/setup', methods=['POST'])
@jwt_required()
def setup_wallet():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return jsonify({'error': 'المحفظة غير موجودة'}), 404
        
        # إعداد معلومات المحفظة
        if 'jib_wallet' in data:
            wallet.jib_wallet = data['jib_wallet']
        if 'jawaly_wallet' in data:
            wallet.jawaly_wallet = data['jawaly_wallet']
        if 'mobile_money_wallet' in data:
            wallet.mobile_money_wallet = data['mobile_money_wallet']
        if 'shamel_money_wallet' in data:
            wallet.shamel_money_wallet = data['shamel_money_wallet']
        if 'fulusik_wallet' in data:
            wallet.fulusik_wallet = data['fulusik_wallet']
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم إعداد المحفظة بنجاح',
            'wallet': wallet.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
