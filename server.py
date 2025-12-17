from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import random
import string
from functools import wraps
import uuid
from bson import ObjectId
try:
    from pymongo import MongoClient
    HAS_MONGO = True
except:
    HAS_MONGO = False
    print("MongoDB not available, using local storage")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'qat-app-secret-key-2024')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-qat-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

CORS(app, supports_credentials=True)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# In-memory database (for testing)
if not HAS_MONGO:
    users_db = []
    products_db = []
    orders_db = []
    markets_db = []
    drivers_db = []
    washing_stations_db = []
    wallets_db = []
    notifications_db = []
    reviews_db = []
    advertisements_db = []
    packages_db = []
    transactions_db = []
else:
    # MongoDB connection
    mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/qat_app')
    client = MongoClient(mongo_uri)
    db = client.qat_app
    users_db = db.users
    products_db = db.products
    orders_db = db.orders
    markets_db = db.markets
    drivers_db = db.drivers
    washing_stations_db = db.washing_stations
    wallets_db = db.wallets
    notifications_db = db.notifications
    reviews_db = db.reviews
    advertisements_db = db.advertisements
    packages_db = db.packages
    transactions_db = db.transactions

# Initialize sample data
def init_sample_data():
    if not HAS_MONGO:
        # Admin user
        admin_user = {
            'id': str(uuid.uuid4()),
            'name': 'المدير العام',
            'email': 'admin@qaty.com',
            'phone': '771234567',
            'password': generate_password_hash('admin123'),
            'user_type': 'admin',
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        users_db.append(admin_user)
        
        # Sample market
        market = {
            'id': str(uuid.uuid4()),
            'name': 'سوق صنعاء المركزي',
            'location': 'صنعاء، اليمن',
            'coordinates': {'lat': 15.3694, 'lng': 44.1910},
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        markets_db.append(market)
        
        # Sample washing station
        washing_station = {
            'id': str(uuid.uuid4()),
            'name': 'مغسلة القات المركزية',
            'market_id': market['id'],
            'location': 'داخل السوق',
            'phone': '771234568',
            'washing_price': 100,
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        washing_stations_db.append(washing_station)
        
        # Sample driver
        driver = {
            'id': str(uuid.uuid4()),
            'name': 'أحمد محمد',
            'phone': '771234569',
            'vehicle_type': 'دراجة نارية',
            'vehicle_number': 'صنعاء 1234',
            'market_id': market['id'],
            'status': 'available',
            'rating': 4.5,
            'total_deliveries': 0,
            'created_at': datetime.now().isoformat()
        }
        drivers_db.append(driver)

# Helper functions
def find_user_by_email(email):
    if HAS_MONGO:
        return users_db.find_one({'email': email})
    else:
        return next((u for u in users_db if u['email'] == email), None)

def find_user_by_id(user_id):
    if HAS_MONGO:
        return users_db.find_one({'id': user_id})
    else:
        return next((u for u in users_db if u['id'] == user_id), None)

def save_user(user):
    if HAS_MONGO:
        users_db.update_one({'id': user['id']}, {'$set': user}, upsert=True)
    else:
        for i, u in enumerate(users_db):
            if u['id'] == user['id']:
                users_db[i] = user
                return
        users_db.append(user)

def save_product(product):
    if HAS_MONGO:
        products_db.update_one({'id': product['id']}, {'$set': product}, upsert=True)
    else:
        for i, p in enumerate(products_db):
            if p['id'] == product['id']:
                products_db[i] = product
                return
        products_db.append(product)

def save_order(order):
    if HAS_MONGO:
        orders_db.update_one({'id': order['id']}, {'$set': order}, upsert=True)
    else:
        for i, o in enumerate(orders_db):
            if o['id'] == order['id']:
                orders_db[i] = order
                return
        orders_db.append(order)

def create_notification(user_id, title, message, notification_type):
    notification = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'title': title,
        'message': message,
        'type': notification_type,
        'read': False,
        'created_at': datetime.now().isoformat()
    }
    if HAS_MONGO:
        notifications_db.insert_one(notification)
    else:
        notifications_db.append(notification)
    
    # Emit socket notification
    socketio.emit(f'notification_{user_id}', notification)
    return notification

# Routes
@app.route('/')
def index():
    return jsonify({'status': 'success', 'message': 'Qat App API is running'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    required_fields = ['name', 'email', 'phone', 'password', 'user_type']
    
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'جميع الحقول مطلوبة'}), 400
    
    if find_user_by_email(data['email']):
        return jsonify({'status': 'error', 'message': 'البريد الإلكتروني مستخدم مسبقاً'}), 400
    
    user = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'password': generate_password_hash(data['password']),
        'user_type': data['user_type'],
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'profile_image': data.get('profile_image', ''),
        'market_id': data.get('market_id', ''),
        'store_name': data.get('store_name', ''),
        'vehicle_type': data.get('vehicle_type', '')
    }
    
    save_user(user)
    
    # Create wallet for user
    wallet = {
        'id': str(uuid.uuid4()),
        'user_id': user['id'],
        'balance': 0.0,
        'phone': data['phone'],
        'created_at': datetime.now().isoformat()
    }
    if HAS_MONGO:
        wallets_db.insert_one(wallet)
    else:
        wallets_db.append(wallet)
    
    access_token = create_access_token(identity=user['id'])
    
    return jsonify({
        'status': 'success',
        'message': 'تم إنشاء الحساب بنجاح',
        'token': access_token,
        'user': {k: v for k, v in user.items() if k != 'password'}
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'status': 'error', 'message': 'البريد الإلكتروني وكلمة المرور مطلوبان'}), 400
    
    user = find_user_by_email(email)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'status': 'error', 'message': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'}), 401
    
    if user.get('status') != 'active':
        return jsonify({'status': 'error', 'message': 'الحساب غير مفعل'}), 403
    
    access_token = create_access_token(identity=user['id'])
    
    return jsonify({
        'status': 'success',
        'message': 'تم تسجيل الدخول بنجاح',
        'token': access_token,
        'user': {k: v for k, v in user.items() if k != 'password'}
    })

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = find_user_by_id(user_id)
    
    if not user:
        return jsonify({'status': 'error', 'message': 'المستخدم غير موجود'}), 404
    
    return jsonify({
        'status': 'success',
        'user': {k: v for k, v in user.items() if k != 'password'}
    })

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    seller_id = request.args.get('seller_id')
    market_id = request.args.get('market_id')
    
    if HAS_MONGO:
        query = {}
        if category:
            query['category'] = category
        if seller_id:
            query['seller_id'] = seller_id
        if market_id:
            query['market_id'] = market_id
        
        products = list(products_db.find(query))
        # Convert ObjectId to string for JSON serialization
        for p in products:
            p['_id'] = str(p['_id'])
    else:
        products = products_db
    
    return jsonify({
        'status': 'success',
        'products': products
    })

@app.route('/api/products', methods=['POST'])
@jwt_required()
def create_product():
    user_id = get_jwt_identity()
    user = find_user_by_id(user_id)
    
    if user['user_type'] not in ['seller', 'admin']:
        return jsonify({'status': 'error', 'message': 'ليس لديك صلاحية لإضافة منتجات'}), 403
    
    data = request.json
    required_fields = ['name', 'price', 'category', 'description']
    
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'جميع الحقول المطلوبة'}), 400
    
    product = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'description': data['description'],
        'price': float(data['price']),
        'category': data['category'],
        'seller_id': user_id,
        'seller_name': user['name'],
        'market_id': user.get('market_id', ''),
        'images': data.get('images', []),
        'stock': int(data.get('stock', 100)),
        'washing_available': data.get('washing_available', True),
        'washing_price': 100.0,
        'rating': 0.0,
        'total_ratings': 0,
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }
    
    save_product(product)
    
    return jsonify({
        'status': 'success',
        'message': 'تم إضافة المنتج بنجاح',
        'product': product
    })

@app.route('/api/orders', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.json
    
    required_fields = ['items', 'delivery_address', 'payment_method']
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'جميع الحقول المطلوبة'}), 400
    
    # Calculate total
    total = 0
    items = []
    sellers = set()
    
    for item in data['items']:
        if HAS_MONGO:
            product = products_db.find_one({'id': item['product_id']})
        else:
            product = next((p for p in products_db if p['id'] == item['product_id']), None)
        
        if not product:
            return jsonify({'status': 'error', 'message': f"المنتج {item['product_id']} غير موجود"}), 404
        
        item_total = product['price'] * item['quantity']
        if item.get('washing', False) and product['washing_available']:
            item_total += product['washing_price']
        
        total += item_total
        sellers.add(product['seller_id'])
        
        items.append({
            'product_id': product['id'],
            'product_name': product['name'],
            'quantity': item['quantity'],
            'price': product['price'],
            'washing': item.get('washing', False),
            'washing_price': product['washing_price'] if item.get('washing', False) else 0,
            'subtotal': item_total
        })
    
    # Check user wallet balance
    if HAS_MONGO:
        wallet = wallets_db.find_one({'user_id': user_id})
    else:
        wallet = next((w for w in wallets_db if w['user_id'] == user_id), None)
    
    if not wallet or wallet['balance'] < total:
        return jsonify({'status': 'error', 'message': 'رصيدك غير كافي'}), 400
    
    # Deduct from wallet
    wallet['balance'] -= total
    if HAS_MONGO:
        wallets_db.update_one({'user_id': user_id}, {'$set': wallet})
    
    # Create order
    order = {
        'id': str(uuid.uuid4()),
        'order_code': ''.join(random.choices(string.digits, k=6)),
        'user_id': user_id,
        'items': items,
        'total': total,
        'delivery_address': data['delivery_address'],
        'payment_method': data['payment_method'],
        'status': 'pending',
        'washing_needed': any(item.get('washing', False) for item in data['items']),
        'market_id': data.get('market_id', ''),
        'created_at': datetime.now().isoformat(),
        'estimated_delivery': (datetime.now() + timedelta(hours=2)).isoformat()
    }
    
    save_order(order)
    
    # Create transaction record
    transaction = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'order_id': order['id'],
        'amount': total,
        'type': 'purchase',
        'status': 'completed',
        'created_at': datetime.now().isoformat()
    }
    if HAS_MONGO:
        transactions_db.insert_one(transaction)
    else:
        transactions_db.append(transaction)
    
    # Notify sellers
    for seller_id in sellers:
        create_notification(
            seller_id,
            'طلب جديد',
            f'لديك طلب جديد برقم #{order["order_code"]}',
            'new_order'
        )
        
        # Add to seller's wallet
        seller_total = sum(item['subtotal'] for item in items 
                          if next((p for p in items if p['product_id'] == item['product_id']), {}).get('seller_id') == seller_id)
        
        if HAS_MONGO:
            seller_wallet = wallets_db.find_one({'user_id': seller_id})
        else:
            seller_wallet = next((w for w in wallets_db if w['user_id'] == seller_id), None)
        
        if seller_wallet:
            seller_wallet['balance'] += seller_total
            if HAS_MONGO:
                wallets_db.update_one({'user_id': seller_id}, {'$set': seller_wallet})
    
    return jsonify({
        'status': 'success',
        'message': 'تم إنشاء الطلب بنجاح',
        'order': order
    })

@app.route('/api/wallet/topup', methods=['POST'])
@jwt_required()
def topup_wallet():
    user_id = get_jwt_identity()
    data = request.json
    
    amount = data.get('amount')
    method = data.get('method')
    reference = data.get('reference')
    
    if not amount or not method:
        return jsonify({'status': 'error', 'message': 'المبلغ وطريقة الدفع مطلوبان'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'status': 'error', 'message': 'المبلغ يجب أن يكون أكبر من صفر'}), 400
    except:
        return jsonify({'status': 'error', 'message': 'المبلغ غير صحيح'}), 400
    
    # In real app, verify payment with payment gateway
    # For demo, we'll just add the amount
    
    if HAS_MONGO:
        wallet = wallets_db.find_one({'user_id': user_id})
    else:
        wallet = next((w for w in wallets_db if w['user_id'] == user_id), None)
    
    if not wallet:
        wallet = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'balance': 0.0
        }
    
    wallet['balance'] += amount
    
    if HAS_MONGO:
        wallets_db.update_one({'user_id': user_id}, {'$set': wallet}, upsert=True)
    else:
        for i, w in enumerate(wallets_db):
            if w['user_id'] == user_id:
                wallets_db[i] = wallet
                break
        else:
            wallets_db.append(wallet)
    
    # Create transaction
    transaction = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'amount': amount,
        'type': 'deposit',
        'method': method,
        'reference': reference,
        'status': 'completed',
        'created_at': datetime.now().isoformat()
    }
    if HAS_MONGO:
        transactions_db.insert_one(transaction)
    else:
        transactions_db.append(transaction)
    
    return jsonify({
        'status': 'success',
        'message': f'تم شحن {amount} ريال بنجاح',
        'new_balance': wallet['balance']
    })

@app.route('/api/wallet/withdraw', methods=['POST'])
@jwt_required()
def withdraw_wallet():
    user_id = get_jwt_identity()
    data = request.json
    
    amount = data.get('amount')
    wallet_info = data.get('wallet_info', {})
    
    if not amount or not wallet_info.get('phone') or not wallet_info.get('wallet_type'):
        return jsonify({'status': 'error', 'message': 'جميع الحقول مطلوبة'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'status': 'error', 'message': 'المبلغ يجب أن يكون أكبر من صفر'}), 400
    except:
        return jsonify({'status': 'error', 'message': 'المبلغ غير صحيح'}), 400
    
    if HAS_MONGO:
        wallet = wallets_db.find_one({'user_id': user_id})
    else:
        wallet = next((w for w in wallets_db if w['user_id'] == user_id), None)
    
    if not wallet or wallet['balance'] < amount:
        return jsonify({'status': 'error', 'message': 'رصيدك غير كافي'}), 400
    
    # In real app, process withdrawal to external wallet
    # For demo, we'll just deduct the amount
    
    wallet['balance'] -= amount
    
    if HAS_MONGO:
        wallets_db.update_one({'user_id': user_id}, {'$set': wallet})
    
    # Create transaction
    transaction = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'amount': -amount,
        'type': 'withdrawal',
        'method': wallet_info['wallet_type'],
        'status': 'pending',  # Needs admin approval in real app
        'wallet_info': wallet_info,
        'created_at': datetime.now().isoformat()
    }
    if HAS_MONGO:
        transactions_db.insert_one(transaction)
    else:
        transactions_db.append(transaction)
    
    return jsonify({
        'status': 'success',
        'message': 'تم تقديم طلب السحب بنجاح، سيتم المعالجة خلال 24 ساعة',
        'new_balance': wallet['balance']
    })

@app.route('/api/admin/drivers', methods=['POST'])
@jwt_required()
def create_driver():
    user_id = get_jwt_identity()
    user = find_user_by_id(user_id)
    
    if user['user_type'] != 'admin':
        return jsonify({'status': 'error', 'message': 'غير مصرح'}), 403
    
    data = request.json
    required_fields = ['name', 'phone', 'vehicle_type', 'market_id']
    
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'جميع الحقول المطلوبة'}), 400
    
    driver = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'phone': data['phone'],
        'vehicle_type': data['vehicle_type'],
        'vehicle_number': data.get('vehicle_number', ''),
        'market_id': data['market_id'],
        'status': 'available',
        'rating': 0.0,
        'total_deliveries': 0,
        'created_at': datetime.now().isoformat()
    }
    
    if HAS_MONGO:
        drivers_db.insert_one(driver)
    else:
        drivers_db.append(driver)
    
    return jsonify({
        'status': 'success',
        'message': 'تم إضافة المندوب بنجاح',
        'driver': driver
    })

@app.route('/api/admin/markets', methods=['POST'])
@jwt_required()
def create_market():
    user_id = get_jwt_identity()
    user = find_user_by_id(user_id)
    
    if user['user_type'] != 'admin':
        return jsonify({'status': 'error', 'message': 'غير مصرح'}), 403
    
    data = request.json
    required_fields = ['name', 'location']
    
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'جميع الحقول المطلوبة'}), 400
    
    market = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'location': data['location'],
        'coordinates': data.get('coordinates', {}),
        'description': data.get('description', ''),
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }
    
    if HAS_MONGO:
        markets_db.insert_one(market)
    else:
        markets_db.append(market)
    
    return jsonify({
        'status': 'success',
        'message': 'تم إضافة السوق بنجاح',
        'market': market
    })

@app.route('/api/admin/washing-stations', methods=['POST'])
@jwt_required()
def create_washing_station():
    user_id = get_jwt_identity()
    user = find_user_by_id(user_id)
    
    if user['user_type'] != 'admin':
        return jsonify({'status': 'error', 'message': 'غير مصرح'}), 403
    
    data = request.json
    required_fields = ['name', 'market_id', 'location']
    
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'جميع الحقول المطلوبة'}), 400
    
    washing_station = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'market_id': data['market_id'],
        'location': data['location'],
        'phone': data.get('phone', ''),
        'washing_price': float(data.get('washing_price', 100)),
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }
    
    if HAS_MONGO:
        washing_stations_db.insert_one(washing_station)
    else:
        washing_stations_db.append(washing_station)
    
    return jsonify({
        'status': 'success',
        'message': 'تم إضافة مغسلة القات بنجاح',
        'washing_station': washing_station
    })

@app.route('/api/admin/advertisements', methods=['POST'])
@jwt_required()
def create_advertisement():
    user_id = get_jwt_identity()
    user = find_user_by_id(user_id)
    
    if user['user_type'] != 'admin':
        return jsonify({'status': 'error', 'message': 'غير مصرح'}), 403
    
    data = request.json
    required_fields = ['title', 'content', 'type', 'target_audience']
    
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'جميع الحقول المطلوبة'}), 400
    
    advertisement = {
        'id': str(uuid.uuid4()),
        'title': data['title'],
        'content': data['content'],
        'type': data['type'],  # banner, popup, interstitial
        'target_audience': data['target_audience'],  # all, buyers, sellers
        'image_url': data.get('image_url', ''),
        'start_date': data.get('start_date', datetime.now().isoformat()),
        'end_date': data.get('end_date', (datetime.now() + timedelta(days=30)).isoformat()),
        'status': 'active',
        'created_by': user_id,
        'created_at': datetime.now().isoformat()
    }
    
    if HAS_MONGO:
        advertisements_db.insert_one(advertisement)
    else:
        advertisements_db.append(advertisement)
    
    return jsonify({
        'status': 'success',
        'message': 'تم إنشاء الإعلان بنجاح',
        'advertisement': advertisement
    })

@app.route('/api/admin/packages', methods=['POST'])
@jwt_required()
def create_package():
    user_id = get_jwt_identity()
    user = find_user_by_id(user_id)
    
    if user['user_type'] != 'admin':
        return jsonify({'status': 'error', 'message': 'غير مصرح'}), 403
    
    data = request.json
    required_fields = ['name', 'price', 'duration_days', 'features']
    
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'جميع الحقول المطلوبة'}), 400
    
    package = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'description': data.get('description', ''),
        'price': float(data['price']),
        'duration_days': int(data['duration_days']),
        'features': data['features'],
        'type': data.get('type', 'advertisement'),  # advertisement, subscription
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }
    
    if HAS_MONGO:
        packages_db.insert_one(package)
    else:
        packages_db.append(package)
    
    return jsonify({
        'status': 'success',
        'message': 'تم إنشاء الباقة بنجاح',
        'package': package
    })

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    
    if HAS_MONGO:
        notifications = list(notifications_db.find({'user_id': user_id}).sort('created_at', -1).limit(50))
        for n in notifications:
            n['_id'] = str(n['_id'])
    else:
        notifications = [n for n in notifications_db if n['user_id'] == user_id]
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        notifications = notifications[:50]
    
    return jsonify({
        'status': 'success',
        'notifications': notifications
    })

@app.route('/api/reviews', methods=['POST'])
@jwt_required()
def create_review():
    user_id = get_jwt_identity()
    data = request.json
    
    required_fields = ['target_id', 'target_type', 'rating', 'comment']
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'جميع الحقول المطلوبة'}), 400
    
    review = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'target_id': data['target_id'],
        'target_type': data['target_type'],  # product, seller, driver
        'rating': float(data['rating']),
        'comment': data['comment'],
        'created_at': datetime.now().isoformat()
    }
    
    if HAS_MONGO:
        reviews_db.insert_one(review)
    else:
        reviews_db.append(review)
    
    # Update average rating
    if data['target_type'] == 'product':
        if HAS_MONGO:
            product_reviews = list(reviews_db.find({'target_id': data['target_id'], 'target_type': 'product'}))
        else:
            product_reviews = [r for r in reviews_db if r['target_id'] == data['target_id'] and r['target_type'] == 'product']
        
        if product_reviews:
            avg_rating = sum(r['rating'] for r in product_reviews) / len(product_reviews)
            if HAS_MONGO:
                products_db.update_one({'id': data['target_id']}, {'$set': {
                    'rating': avg_rating,
                    'total_ratings': len(product_reviews)
                }})
            else:
                for p in products_db:
                    if p['id'] == data['target_id']:
                        p['rating'] = avg_rating
                        p['total_ratings'] = len(product_reviews)
                        break
    
    return jsonify({
        'status': 'success',
        'message': 'تم إضافة التقييم بنجاح',
        'review': review
    })

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    user_id = get_jwt_identity()
    data = request.json
    
    new_status = data.get('status')
    if not new_status:
        return jsonify({'status': 'error', 'message': 'الحالة مطلوبة'}), 400
    
    if HAS_MONGO:
        order = orders_db.find_one({'id': order_id})
    else:
        order = next((o for o in orders_db if o['id'] == order_id), None)
    
    if not order:
        return jsonify({'status': 'error', 'message': 'الطلب غير موجود'}), 404
    
    # Check permissions
    user = find_user_by_id(user_id)
    if user['user_type'] not in ['admin', 'seller'] and order['user_id'] != user_id:
        return jsonify({'status': 'error', 'message': 'غير مصرح'}), 403
    
    order['status'] = new_status
    order['updated_at'] = datetime.now().isoformat()
    
    save_order(order)
    
    # Send notifications based on status change
    if new_status == 'confirmed':
        create_notification(
            order['user_id'],
            'تم تأكيد طلبك',
            f'تم تأكيد طلبك #{order["order_code"]}',
            'order_update'
        )
    elif new_status == 'washing':
        # Notify washing station
        create_notification(
            'washing_station',  # In real app, find washing station manager
            'طلب غسيل جديد',
            f'طلب غسيل جديد #{order["order_code"]}',
            'washing_request'
        )
    elif new_status == 'delivering':
        # Assign driver and notify
        if order.get('market_id'):
            if HAS_MONGO:
                available_drivers = list(drivers_db.find({
                    'market_id': order['market_id'],
                    'status': 'available'
                }))
            else:
                available_drivers = [d for d in drivers_db 
                                   if d['market_id'] == order['market_id'] and d['status'] == 'available']
            
            if available_drivers:
                driver = random.choice(available_drivers)
                order['driver_id'] = driver['id']
                order['driver_name'] = driver['name']
                
                create_notification(
                    driver['id'],
                    'طلب توصيل جديد',
                    f'لديك طلب توصيل جديد #{order["order_code"]}',
                    'delivery_assigned'
                )
    
    return jsonify({
        'status': 'success',
        'message': f'تم تحديث حالة الطلب إلى {new_status}',
        'order': order
    })

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Initialize sample data
init_sample_data()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
