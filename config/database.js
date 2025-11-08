// كود إنشاء الجداول
const createTables = async (pool) => {
    try {
        // جدول المستخدمين
        await pool.execute(`
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                password VARCHAR(255) NOT NULL,
                user_type ENUM('buyer', 'seller', 'driver') NOT NULL,
                profile_image VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // جدول البائعين
        await pool.execute(`
            CREATE TABLE IF NOT EXISTS sellers (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                store_name VARCHAR(100),
                description TEXT,
                location VARCHAR(100),
                rating DECIMAL(3,2) DEFAULT 0,
                total_sales INT DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        `);

        // جدول السائقين
        await pool.execute(`
            CREATE TABLE IF NOT EXISTS drivers (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                vehicle_type VARCHAR(50),
                vehicle_number VARCHAR(20),
                license_number VARCHAR(50),
                is_available BOOLEAN DEFAULT TRUE,
                current_location VARCHAR(100),
                rating DECIMAL(3,2) DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        `);

        // جدول المنتجات
        await pool.execute(`
            CREATE TABLE IF NOT EXISTS products (
                id INT PRIMARY KEY AUTO_INCREMENT,
                seller_id INT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                category ENUM('premium', 'good', 'organic') NOT NULL,
                image_url VARCHAR(255),
                stock_quantity INT DEFAULT 0,
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE
            )
        `);

        // جدول الطلبات
        await pool.execute(`
            CREATE TABLE IF NOT EXISTS orders (
                id INT PRIMARY KEY AUTO_INCREMENT,
                buyer_id INT,
                seller_id INT,
                driver_id INT,
                total_amount DECIMAL(10,2) NOT NULL,
                status ENUM('pending', 'confirmed', 'preparing', 'ready', 'picked_up', 'delivered', 'cancelled') DEFAULT 'pending',
                delivery_address TEXT NOT NULL,
                delivery_lat DECIMAL(10,8),
                delivery_lng DECIMAL(11,8),
                payment_method ENUM('jib', 'jawaly', 'kureemy', 'wallet'),
                payment_status ENUM('pending', 'paid', 'failed') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (buyer_id) REFERENCES users(id),
                FOREIGN KEY (seller_id) REFERENCES sellers(id),
                FOREIGN KEY (driver_id) REFERENCES drivers(id)
            )
        `);

        // جدول عناصر الطلب
        await pool.execute(`
            CREATE TABLE IF NOT EXISTS order_items (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT,
                product_id INT,
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        `);

        // جدول المحفظة الإلكترونية
        await pool.execute(`
            CREATE TABLE IF NOT EXISTS wallets (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                balance DECIMAL(10,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        `);

        console.log('All tables created successfully');
    } catch (error) {
        console.error('Error creating tables:', error);
    }
};

module.exports = { createTables };
