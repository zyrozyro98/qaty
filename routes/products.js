module.exports = (pool) => {
    const router = require('express').Router();

    // الحصول على جميع المنتجات
    router.get('/', async (req, res) => {
        try {
            const { category, min_price, max_price, location } = req.query;
            
            let query = `
                SELECT p.*, s.store_name, s.location as seller_location 
                FROM products p 
                JOIN sellers s ON p.seller_id = s.id 
                WHERE p.is_available = TRUE
            `;
            let params = [];

            if (category) {
                query += ' AND p.category = ?';
                params.push(category);
            }

            if (min_price) {
                query += ' AND p.price >= ?';
                params.push(min_price);
            }

            if (max_price) {
                query += ' AND p.price <= ?';
                params.push(max_price);
            }

            if (location) {
                query += ' AND s.location = ?';
                params.push(location);
            }

            query += ' ORDER BY p.created_at DESC';

            const [products] = await pool.execute(query, params);
            res.json(products);

        } catch (error) {
            console.error(error);
            res.status(500).json({ error: 'خطأ في السيرفر' });
        }
    });

    // إضافة منتج جديد (للبائعين)
    router.post('/', async (req, res) => {
        try {
            const { name, description, price, category, stock_quantity, image_url, seller_id } = req.body;

            const [result] = await pool.execute(
                `INSERT INTO products (seller_id, name, description, price, category, stock_quantity, image_url) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)`,
                [seller_id, name, description, price, category, stock_quantity, image_url]
            );

            res.json({
                message: 'تم إضافة المنتج بنجاح',
                productId: result.insertId
            });

        } catch (error) {
            console.error(error);
            res.status(500).json({ error: 'خطأ في السيرفر' });
        }
    });

    // تحديث منتج
    router.put('/:id', async (req, res) => {
        try {
            const productId = req.params.id;
            const { name, description, price, category, stock_quantity, image_url } = req.body;

            await pool.execute(
                `UPDATE products SET name=?, description=?, price=?, category=?, stock_quantity=?, image_url=?
                 WHERE id=?`,
                [name, description, price, category, stock_quantity, image_url, productId]
            );

            res.json({ message: 'تم تحديث المنتج بنجاح' });

        } catch (error) {
            console.error(error);
            res.status(500).json({ error: 'خطأ في السيرفر' });
        }
    });

    return router;
};
