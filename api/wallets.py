from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Wallet, Transaction, User
from datetime import datetime
import random
import string

wallets_bp = Blueprint('wallets', __name__)

def generate_transaction_reference():
    """إنشاء رقم مرجعي للمعاملة"""
    timestamp = datetime.now().strftime('%y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"TXN{timestamp}{random_str}"

@wallets_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    try:
        user_id = get_jwt_identity()
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        
        if not wallet:
            return jsonify({'error': 'المحفظة غير موجودة'}), 404
        
        return jsonify({
            'balance': wallet.balance,
            'wallet': wallet.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wallets_bp.route('/deposit', methods=['POST'])
@jwt_required()
def deposit():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['amount', 'payment_method', 'reference_number']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'حقل {field} مطلوب'}), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'المبلغ يجب أن يكون أكبر من الصفر'}), 400
        
        # الحصول على المحفظة
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return jsonify({'error': 'المحفظة غير موجودة'}), 404
        
        # إضافة المبلغ للمحفظة
        wallet.balance += amount
        
        # تسجيل المعاملة
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            transaction_type='deposit',
            payment_method=data['payment_method'],
            status='completed',
            reference_number=data['reference_number'],
            notes=data.get('notes', f'إيداع عبر {data["payment_method"]}')
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إيداع المبلغ بنجاح',
            'new_balance': wallet.balance,
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@wallets_bp.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['amount', 'wallet_type', 'wallet_number']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'حقل {field} مطلوب'}), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'المبلغ يجب أن يكون أكبر من الصفر'}), 400
        
        # الحصول على المحفظة
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return jsonify({'error': 'المحفظة غير موجودة'}), 404
        
        # التحقق من الرصيد
        if wallet.balance < amount:
            return jsonify({'error': 'رصيد غير كافي'}), 400
        
        # خصم المبلغ
        wallet.balance -= amount
        
        # تسجيل المعاملة
        transaction = Transaction(
            user_id=user_id,
            amount=-amount,
            transaction_type='withdrawal',
            payment_method=data['wallet_type'],
            status='pending',  # تنتظر الموافقة
            reference_number=generate_transaction_reference(),
            notes=f'سحب إلى {data["wallet_type"]}: {data["wallet_number"]}'
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'تم تقديم طلب السحب بنجاح',
            'new_balance': wallet.balance,
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@wallets_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        user_id = get_jwt_identity()
        
        # الحصول على المعاملات
        transactions = Transaction.query.filter_by(user_id=user_id).order_by(
            Transaction.created_at.desc()
        ).limit(50).all()
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions],
            'count': len(transactions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wallets_bp.route('/gift-code/validate', methods=['POST'])
@jwt_required()
def validate_gift_code():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'code' not in data:
            return jsonify({'error': 'كود الهدية مطلوب'}), 400
        
        # هنا يجب الاتصال بخدمة التحقق من أكواد الهدايا
        # هذه مجرد محاكاة
        
        code = data['code'].upper().strip()
        
        # محاكاة التحقق
        if code.startswith('GIFT'):
            amount = 50  # مبلغ افتراضي
            
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if wallet:
                wallet.balance += amount
                
                transaction = Transaction(
                    user_id=user_id,
                    amount=amount,
                    transaction_type='gift',
                    payment_method='gift_code',
                    status='completed',
                    reference_number=code,
                    notes='كود هدية'
                )
                db.session.add(transaction)
                db.session.commit()
                
                return jsonify({
                    'message': 'تم تفعيل كود الهدية بنجاح',
                    'amount': amount,
                    'new_balance': wallet.balance
                }), 200
            else:
                return jsonify({'error': 'المحفظة غير موجودة'}), 404
        else:
            return jsonify({'error': 'كود الهدية غير صالح'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@wallets_bp.route('/deposit/instructions', methods=['GET'])
def get_deposit_instructions():
    """الحصول على تعليمات الإيداع"""
    
    instructions = {
        'bank_transfer': {
            'title': 'التحويل البنكي',
            'account_name': 'يوسف محمد علي حمود زهير',
            'account_number': '771831482',
            'bank_name': 'البنك المركزي اليمني',
            'notes': 'أرسل الحوالة مع الاحتفاظ برقم المرجع'
        },
        'mobile_wallets': [
            {
                'name': 'محفظة جيب',
                'number': '771831482',
                'instructions': 'أرسل المبلغ إلى الرقم المذكور'
            },
            {
                'name': 'محفظة جوالي',
                'number': '771831482',
                'instructions': 'أرسل المبلغ إلى الرقم المذكور'
            },
            {
                'name': 'محفظة موبايل موني',
                'number': '771831482',
                'instructions': 'أرسل المبلغ إلى الرقم المذكور'
            },
            {
                'name': 'محفظة الشامل موني',
                'number': '771831482',
                'instructions': 'أرسل المبلغ إلى الرقم المذكور'
            },
            {
                'name': 'محفظة فلوسك',
                'number': '771831482',
                'instructions': 'أرسل المبلغ إلى الرقم المذكور'
            }
        ],
        'important_notes': [
            'احتفظ برقم المرجع عند الإيداع',
            'سيتم إضافة المبلغ خلال 24 ساعة',
            'للأسئلة اتصل بالدعم الفني'
        ]
    }
    
    return jsonify(instructions), 200
