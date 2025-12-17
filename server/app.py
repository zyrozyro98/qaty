# -*- coding: utf-8 -*-
"""
سيرفر API لتطبيق قات
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import sqlite3
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# إعدادات JWT
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

def get_db_connection():
    """الاتصال بقاعدة البيانات"""
    conn = sqlite3.connect('qat_database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    """فحص حالة السيرفر"""
    return jsonify({'status': 'healthy', 'message': 'Qat API is running'})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """تسجيل مستخدم جديد"""
    data = request.get_json()
    
    # التحقق من البيانات
    required_fields = ['username', 'password', 'full_name', 'email', 'phone', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'حقل {field} مطلوب'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # التحقق من عدم تكرار اسم المستخدم أو البريد
    cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', 
                   (data['username'], data['email']))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({'success': False, 'message': 'اسم المستخدم أو البريد الإلكتروني موجود مسبقاً'}), 400
    
    try:
        # إدخال المستخدم الجديد
        cursor.execute('''
            INSERT INTO users (username, password, full_name, email, phone, role, 
                             store_name, vehicle_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['username'],
            data['password'],  # في التطبيق الحقيقي، يجب تشفير كلمة المرور
            data['full_name'],
            data['email'],
            data['phone'],
            data['role'],
            data.get('store_name', ''),
            data.get('vehicle_type', ''),
            datetime.now().isoformat()
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # إنشاء token
        access_token = create_access_token(identity={'id': user_id, 'username': data['username']})
        
        # إرجاع بيانات المستخدم
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = dict(cursor.fetchone())
        
        # إخفاء كلمة المرور
        user.pop('password', None)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء الحساب بنجاح',
            'user': user,
            'token': access_token
        }), 201
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """تسجيل الدخول"""
    data = request.get_json()
    
    if 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                   (data['username'], data['password']))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'}), 401
    
    # إنشاء token
    user_dict = dict(user)
    access_token = create_access_token(identity={'id': user_dict['id'], 'username': user_dict['username']})
    
    # إخفاء كلمة المرور
    user_dict.pop('password', None)
    
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'تم تسجيل الدخول بنجاح',
        'user': user_dict,
        'token': access_token
    })

@app.route('/api/products', methods=['GET'])
@jwt_required()
def get_products():
    """جلب جميع المنتجات"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # الحصول على معلمات التصفية
    category = request.args.get('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    seller_id = request.args.get('seller_id')
    
    # بناء الاستعلام
    query = '''
        SELECT p.*, u.store_name, u.rating as seller_rating 
        FROM products p 
        JOIN users u ON p.seller_id = u.id 
        WHERE p.is_available = 1 AND p.quantity > 0
    '''
    params = []
    
    if category:
        query += ' AND p.category = ?'
        params.append(category)
    
    if min_price:
        query += ' AND p.price >= ?'
        params.append(float(min_price))
    
    if max_price:
        query += ' AND p.price <= ?'
        params.append(float(max_price))
    
    if seller_id:
        query += ' AND p.seller_id = ?'
        params.append(int(seller_id))
    
    query += ' ORDER BY p.created_at DESC'
    
    cursor.execute(query, params)
    products = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({'success': True, 'products': products})

@app.route('/api/orders/create', methods=['POST'])
@jwt_required()
def create_order():
    """إنشاء طلب جديد"""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['product_id', 'quantity', 'washing_required', 'delivery_address', 'payment_method']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'حقل {field} مطلوب'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # التحقق من المنتج
        cursor.execute('SELECT * FROM products WHERE id = ? AND is_available = 1', 
                       (data['product_id'],))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            return jsonify({'success': False, 'message': 'المنتج غير متوفر'}), 400
        
        product = dict(product)
        
        # التحقق من الكمية المتاحة
        if product['quantity'] < data['quantity']:
            conn.close()
            return jsonify({'success': False, 'message': 'الكمية غير متوفرة'}), 400
        
        # حساب السعر
        washing_price = 100 if data['washing_required'] else 0
        total_price = product['price'] * data['quantity']
        final_price = total_price + washing_price
        
        # توليد كود الطلب
        import random
        from datetime import datetime
        order_code = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        # إنشاء الطلب
        cursor.execute('''
            INSERT INTO orders 
            (order_code, buyer_id, seller_id, product_id, quantity, total_price, 
             washing_price, final_price, washing_required, market_id, 
             delivery_address, payment_method, status, estimated_delivery, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'confirmed', ?, ?)
        ''', (
            order_code,
            current_user['id'],
            product['seller_id'],
            data['product_id'],
            data['quantity'],
            total_price,
            washing_price,
            final_price,
            data['washing_required'],
            product.get('market_id', 1),
            data['delivery_address'],
            data['payment_method'],
            (datetime.now() + timedelta(hours=1)).isoformat(),
            datetime.now().isoformat()
        ))
        
        order_id = cursor.lastrowid
        
        # تحديث كمية المنتج
        cursor.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?', 
                       (data['quantity'], data['product_id']))
        
        # خصم المبلغ من رصيد المشتري (إذا كان الدفع بالرصيد)
        if data['payment_method'] == 'wallet':
            cursor.execute('UPDATE users SET wallet_balance = wallet_balance - ? WHERE id = ?', 
                           (final_price, current_user['id']))
        
        # إضافة المبلغ لحساب البائع
        cursor.execute('UPDATE users SET wallet_balance = wallet_balance + ? WHERE id = ?', 
                       (final_price, product['seller_id']))
        
        conn.commit()
        
        # جلب بيانات الطلب الكاملة
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = dict(cursor.fetchone())
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء الطلب بنجاح',
            'order': order
        }), 201
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """جلب إشعارات المستخدم"""
    current_user = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM notifications 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 20
    ''', (current_user['id'],))
    
    notifications = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({'success': True, 'notifications': notifications})

if __name__ == '__main__':
    # إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة
    conn = sqlite3.connect('qat_database.db')
    cursor = conn.cursor()
    
    # إنشاء الجداول (نفس الجداول الموجودة في main.py)
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            wallet_balance REAL DEFAULT 0,
            store_name TEXT,
            vehicle_type TEXT,
            rating REAL DEFAULT 5.0,
            total_ratings INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            image_url TEXT,
            rating REAL DEFAULT 0,
            total_reviews INTEGER DEFAULT 0,
            is_available BOOLEAN DEFAULT 1,
            market_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(id)
        );
        
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT UNIQUE NOT NULL,
            buyer_id INTEGER NOT NULL,
            seller_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            washing_price REAL DEFAULT 0,
            final_price REAL NOT NULL,
            washing_required BOOLEAN DEFAULT 0,
            washer_id INTEGER,
            driver_id INTEGER,
            market_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            payment_method TEXT,
            payment_status TEXT DEFAULT 'pending',
            delivery_address TEXT NOT NULL,
            delivery_notes TEXT,
            estimated_delivery TIMESTAMP,
            actual_delivery TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES users(id),
            FOREIGN KEY (seller_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            data TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    
    conn.commit()
    conn.close()
    
    # تشغيل السيرفر
    app.run(host='0.0.0.0', port=5000, debug=True)
