module.exports = (pool) => {
    const router = require('express').Router();

    // إنشاء طلب جديد
    router.post('/', async (req, res) => {
        const connection = await pool.getConnection();
        try {
            await connection.beginTransaction();

            const { buyer_id, items, delivery_address, payment_method } = req.body;

            // حساب المبلغ الإجمالي
            let totalAmount = 0;
            for (const item of items) {
                const [products] = await connection.execute(
                    'SELECT price FROM products WHERE id = ?',
                    [item.product_id]
                );
                if (products.length === 0) {
                    throw new Error(`المنتج غير موجود: ${item.product_id}`);
                }
                totalAmount += products[0].price * item.quantity;
            }

            // الحصول على seller_id من أول منتج
            const [firstProduct] = await connection.execute(
                'SELECT seller_id FROM products WHERE id = ?',
                [items[0].product_id]
            );
            const seller_id = firstProduct[0].seller_id;

            // إنشاء الطلب
            const [orderResult] = await connection.execute(
                `INSERT INTO orders (buyer_id, seller_id, total_amount, delivery_address, payment_method) 
                 VALUES (?, ?, ?, ?, ?)`,
                [buyer_id, seller_id, totalAmount, delivery_address, payment_method]
            );

            const orderId = orderResult.insertId;

            // إضافة عناصر الطلب
            for (const item of items) {
                const [products] = await connection.execute(
                    'SELECT price FROM products WHERE id = ?',
                    [item.product_id]
                );
                
                await connection.execute(
                    'INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)',
                    [orderId, item.product_id, item.quantity, products[0].price]
                );

                // تحديث المخزون
                await connection.execute(
                    'UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?',
                    [item.quantity, item.product_id]
                );
            }

            await connection.commit();

            res.json({
                message: 'تم إنشاء الطلب بنجاح',
                orderId,
                totalAmount
            });

        } catch (error) {
            await connection.rollback();
            console.error(error);
            res.status(500).json({ error: 'خطأ في إنشاء الطلب' });
        } finally {
            connection.release();
        }
    });

    // الحصول على طلبات المستخدم
    router.get('/user/:userId', async (req, res) => {
        try {
            const userId = req.params.userId;

            const [orders] = await pool.execute(`
                SELECT o.*, s.store_name, u.name as driver_name 
                FROM orders o 
                LEFT JOIN sellers s ON o.seller_id = s.id 
                LEFT JOIN drivers d ON o.driver_id = d.id 
                LEFT JOIN users u ON d.user_id = u.id 
                WHERE o.buyer_id = ? 
                ORDER BY o.created_at DESC
            `, [userId]);

            res.json(orders);

        } catch (error) {
            console.error(error);
            res.status(500).json({ error: 'خطأ في السيرفر' });
        }
    });

    // تحديث حالة الطلب
    router.put('/:id/status', async (req, res) => {
        try {
            const orderId = req.params.id;
            const { status, driver_id } = req.body;

            let query = 'UPDATE orders SET status = ?';
            let params = [status];

            if (driver_id) {
                query += ', driver_id = ?';
                params.push(driver_id);
            }

            query += ' WHERE id = ?';
            params.push(orderId);

            await pool.execute(query, params);

            res.json({ message: 'تم تحديث حالة الطلب بنجاح' });

        } catch (error) {
            console.error(error);
            res.status(500).json({ error: 'خطأ في السيرفر' });
        }
    });

    return router;
};
