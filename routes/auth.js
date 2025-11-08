const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

module.exports = (pool) => {
    const router = require('express').Router();

    // تسجيل مستخدم جديد
    router.post('/register', async (req, res) => {
        try {
            const { name, email, phone, password, user_type, store_name, vehicle_type } = req.body;
            
            // التحقق من وجود المستخدم
            const [existing] = await pool.execute(
                'SELECT id FROM users WHERE email = ?',
                [email]
            );
            
            if (existing.length > 0) {
                return res.status(400).json({ error: 'البريد الإلكتروني مستخدم بالفعل' });
            }

            // تشفير كلمة المرور
            const hashedPassword = await bcrypt.hash(password, 10);

            // إضافة المستخدم
            const [result] = await pool.execute(
                'INSERT INTO users (name, email, phone, password, user_type) VALUES (?, ?, ?, ?, ?)',
                [name, email, phone, hashedPassword, user_type]
            );

            const userId = result.insertId;

            // إضافة بيانات إضافية حسب نوع المستخدم
            if (user_type === 'seller' && store_name) {
                await pool.execute(
                    'INSERT INTO sellers (user_id, store_name) VALUES (?, ?)',
                    [userId, store_name]
                );
            }

            if (user_type === 'driver' && vehicle_type) {
                await pool.execute(
                    'INSERT INTO drivers (user_id, vehicle_type) VALUES (?, ?)',
                    [userId, vehicle_type]
                );
            }

            // إنشاء محفظة للمستخدم
            await pool.execute(
                'INSERT INTO wallets (user_id) VALUES (?)',
                [userId]
            );

            // إنشاء token
            const token = jwt.sign(
                { userId, user_type },
                process.env.JWT_SECRET || 'your-secret-key',
                { expiresIn: '30d' }
            );

            res.json({
                message: 'تم إنشاء الحساب بنجاح',
                token,
                user: {
                    id: userId,
                    name,
                    email,
                    user_type
                }
            });

        } catch (error) {
            console.error(error);
            res.status(500).json({ error: 'خطأ في السيرفر' });
        }
    });

    // تسجيل الدخول
    router.post('/login', async (req, res) => {
        try {
            const { email, password } = req.body;

            // البحث عن المستخدم
            const [users] = await pool.execute(
                'SELECT * FROM users WHERE email = ? AND is_active = TRUE',
                [email]
            );

            if (users.length === 0) {
                return res.status(400).json({ error: 'البريد الإلكتروني أو كلمة المرور غير صحيحة' });
            }

            const user = users[0];

            // التحقق من كلمة المرور
            const isValidPassword = await bcrypt.compare(password, user.password);
            if (!isValidPassword) {
                return res.status(400).json({ error: 'البريد الإلكتروني أو كلمة المرور غير صحيحة' });
            }

            // إنشاء token
            const token = jwt.sign(
                { userId: user.id, user_type: user.user_type },
                process.env.JWT_SECRET || 'your-secret-key',
                { expiresIn: '30d' }
            );

            res.json({
                message: 'تم تسجيل الدخول بنجاح',
                token,
                user: {
                    id: user.id,
                    name: user.name,
                    email: user.email,
                    user_type: user.user_type,
                    phone: user.phone
                }
            });

        } catch (error) {
            console.error(error);
            res.status(500).json({ error: 'خطأ في السيرفر' });
        }
    });

    return router;
};
