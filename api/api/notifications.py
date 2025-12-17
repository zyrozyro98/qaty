from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Notification
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user_id = get_jwt_identity()
        
        # الحصول على الإشعارات
        notifications = Notification.query.filter_by(
            user_id=user_id
        ).order_by(Notification.created_at.desc()).limit(50).all()
        
        return jsonify({
            'notifications': [n.to_dict() for n in notifications],
            'count': len(notifications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/unread', methods=['GET'])
@jwt_required()
def get_unread_notifications():
    try:
        user_id = get_jwt_identity()
        
        # الحصول على الإشعارات غير المقروءة
        notifications = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).order_by(Notification.created_at.desc()).all()
        
        return jsonify({
            'notifications': [n.to_dict() for n in notifications],
            'count': len(notifications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/mark-read', methods=['POST'])
@jwt_required()
def mark_notifications_read():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'notification_ids' not in data:
            return jsonify({'error': 'معرفات الإشعارات مطلوبة'}), 400
        
        # تحديث حالة القراءة
        Notification.query.filter(
            Notification.id.in_(data['notification_ids']),
            Notification.user_id == user_id
        ).update({'is_read': True}, synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({'message': 'تم تحديث حالة الإشعارات'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    try:
        user_id = get_jwt_identity()
        
        # تحديث جميع الإشعارات
        Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True}, synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({'message': 'تم قراءة جميع الإشعارات'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/send', methods=['POST'])
@jwt_required()
def send_notification():
    try:
        user_id = get_jwt_identity()
        
        # التحقق من صلاحية المستخدم (يجب أن يكون مديراً أو لديه صلاحيات)
        # هذه وظيفة مساعدة يجب التحقق منها
        
        data = request.get_json()
        
        required_fields = ['target_user_id', 'title', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'حقل {field} مطلوب'}), 400
        
        # إنشاء الإشعار
        notification = Notification(
            user_id=data['target_user_id'],
            title=data['title'],
            message=data['message'],
            notification_type=data.get('type', 'system'),
            data=data.get('data')
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # هنا يمكن إرسال الإشعار عبر WebSocket
        
        return jsonify({
            'message': 'تم إرسال الإشعار',
            'notification': notification.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
