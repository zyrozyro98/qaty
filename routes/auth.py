"""
مسارات المصادقة
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from __init__ import db
from models import User
import hashlib

bp = Blueprint('auth', __name__)

def hash_password(password):
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

@bp.route('/register', methods=['POST'])
def register():
    """تسجيل مستخدم جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['username', 'password', 'full_name', 'email', 'phone', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'حقل {field} مطلوب'
                }), 400
        
        # التحقق من عدم تكرار المستخدم
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم موجود مسبقاً'
            }), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'البريد الإلكتروني موجود مسبقاً'
            }), 400
        
        if User.query.filter_by(phone=data['phone']).first():
            return jsonify({
                'success': False,
                'message': 'رقم الهاتف موجود مسبقاً'
            }), 400
        
        # إنشاء المستخدم الجديد
        user = User(
            username=data['username'],
            password=hash_password(data['password']),
            full_name=data['full_name'],
            email=data['email'],
            phone=data['phone'],
            role=data['role'],
            store_name=data.get('store_name', ''),
            vehicle_type=data.get('vehicle_type', ''),
            wallet_balance=data.get('wallet_balance', 0.0),
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        # إنشاء token
        access_token = create_access_token(identity={
            'id': user.id,
            'username': user.username,
            'role': user.role
        })
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء الحساب بنجاح',
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'wallet_balance': user.wallet_balance
            },
            'token': access_token
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في التسجيل: {str(e)}'
        }), 500

@bp.route('/login', methods=['POST'])
def login():
    """تسجيل الدخول"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم وكلمة المرور مطلوبان'
            }), 400
        
        # البحث عن المستخدم
        user = User.query.filter_by(username=data['username']).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }), 401
        
        # التحقق من كلمة المرور
        if user.password != hash_password(data['password']):
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }), 401
        
        # التحقق من حالة الحساب
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'الحساب معطل'
            }), 403
        
        # إنشاء token
        access_token = create_access_token(identity={
            'id': user.id,
            'username': user.username,
            'role': user.role
        })
        
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'wallet_balance': user.wallet_balance,
                'store_name': user.store_name,
                'vehicle_type': user.vehicle_type,
                'rating': user.rating
            },
            'token': access_token
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في تسجيل الدخول: {str(e)}'
        }), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """الحصول على الملف الشخصي"""
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user['id'])
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'المستخدم غير موجود'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
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
                'total_ratings': user.total_ratings,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في جلب الملف الشخصي: {str(e)}'
        }), 500

@bp.route('/wallet-info', methods=['GET'])
def wallet_info():
    """الحصول على معلومات المحافظ"""
    try:
        support_phone = '771831482'
        bank_account_name = 'يوسف محمد علي حمود زهير'
        bank_account_number = 'SA1234567890123456789012'
        bank_name = 'البنك الأهلي التجاري'
        
        return jsonify({
            'success': True,
            'wallets': {
                'jib': {
                    'name': 'محفظة جيب',
                    'number': support_phone,
                    'owner': bank_account_name
                },
                'jawaly': {
                    'name': 'محفظة جوالي',
                    'number': support_phone,
                    'owner': bank_account_name
                },
                'mobail_money': {
                    'name': 'محفظة موبايل موني',
                    'number': support_phone,
                    'owner': bank_account_name
                },
                'shamel_money': {
                    'name': 'محفظة الشامل موني',
                    'number': support_phone,
                    'owner': bank_account_name
                },
                'floosak': {
                    'name': 'محفظة فلوسك',
                    'number': support_phone,
                    'owner': bank_account_name
                }
            },
            'bank': {
                'account_name': bank_account_name,
                'account_number': bank_account_number,
                'bank_name': bank_name,
                'phone': support_phone
            },
            'support': {
                'phone': support_phone,
                'email': 'support@qat-app.com'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في جلب معلومات المحافظ: {str(e)}'
        }), 500
