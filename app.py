import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit
from datetime import timedelta
from datetime import datetime
import json
from database import db, init_db
from api.auth import auth_bp
from api.products import products_bp
from api.orders import orders_bp
from api.wallets import wallets_bp
from api.admin import admin_bp
from api.notifications import notifications_bp
from models import User, Product, Order, Wallet, Market, WashingStation, Driver, Advertisement

# تكوين التطبيق
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# تكوين قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///qaty.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'qaty-super-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# تهيئة الامتدادات
db.init_app(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# تسجيل Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(wallets_bp, url_prefix='/api/wallets')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('connected', {'message': 'Connected to Qaty Server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    if room:
        socketio.enter_room(request.sid, room)
        emit('room_joined', {'room': room}, room=room)

# وظائف مساعدة للإشعارات
def notify_user(user_id, title, message, data=None):
    """إرسال إشعار إلى مستخدم معين"""
    socketio.emit(f'notification_{user_id}', {
        'title': title,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/')
def home():
    return jsonify({
        'status': 'success',
        'message': 'Qaty API is running',
        'version': '1.0.0',
        'docs': 'https://github.com/zyrozyro98/qaty'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # محاولة الاتصال بقاعدة البيانات
        db.session.execute('SELECT 1')
        db_status = 'connected'
    except:
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    })

# إنشاء الجداول
with app.app_context():
    db.create_all()
    # إنشاء حساب مدير افتراضي إذا لم يكن موجوداً
    admin = User.query.filter_by(user_type='admin').first()
    if not admin:
        from werkzeug.security import generate_password_hash
        admin = User(
            name="مدير النظام",
            phone="771831482",
            email="admin@qaty.com",
            password=generate_password_hash("Admin@123"),
            user_type="admin"
        )
        db.session.add(admin)
        db.session.commit()
        
        # إنشاء محفظة للمدير
        wallet = Wallet(user_id=admin.id, balance=10000.0)
        db.session.add(wallet)
        db.session.commit()
        
        logger.info("✅ تم إنشاء حساب المدير الافتراضي")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
