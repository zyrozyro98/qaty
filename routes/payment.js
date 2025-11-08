module.exports = (pool) => {
    const router = require('express').Router();

    // شحن المحفظة
    router.post('/wallet/topup', async (req, res) => {
        try {
            const { user_id, amount, payment_method } = req.body;

            await pool.execute(
                'UPDATE wallets SET balance = balance + ? WHERE user_id = ?',
                [amount, user_id]
            );

            res.json({ message: 'تم شحن المحفظة بنجاح' });

        } catch (error) {
            console.error(error);
            res.status(500).json({ error: 'خطأ في عملية الشحن' });
        }
    });

    // الدفع من المحفظة
    router.post('/wallet/pay', async (req, res) => {
        const connection = await pool.getConnection();
        try {
            await connection.beginTransaction();

            const { user_id, order_id, amount } = req.body;

            // التحقق من الرصيد
            const [wallets] = await connection.execute(
                'SELECT balance FROM wallets WHERE user_id = ?',
                [user_id]
            );

            if (wallets.length === 0 || wallets[0].balance < amount) {
                throw new Error('رصيد غير كافي');
            }

            // خصم المبلغ
            await connection.execute(
                'UPDATE wallets SET balance = balance - ? WHERE user_id = ?',
                [amount, user_id]
            );

            // تحديث حالة الطلب
            await connection.execute(
                'UPDATE orders SET payment_status = "paid" WHERE id = ?',
                [order_id]
            );

            await connection.commit();

            res.json({ message: 'تم الدفع بنجاح' });

        } catch (error) {
            await connection.rollback();
            console.error(error);
            res.status(400).json({ error: error.message });
        } finally {
            connection.release();
        }
    });

    return router;
};
