const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const resetPassword = async (req, res) => {
    try {
        const { token, newPassword } = req.body;
        
        // Verify JWT token
        const decoded = jwt.verify(token, process.env.SECRET_KEY);
        const userId = decoded.user_id;
        
        // Hash new password
        const hashedPassword = await bcrypt.hash(newPassword, 10);
        
        // Update user password in database
        const query = 'UPDATE users SET password = ? WHERE id = ?';
        await db.run(query, [hashedPassword, userId]);
        
        res.json({ message: 'Password reset successfully' });
        
    } catch (error) {
        if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
            return res.status(400).json({ error: 'Invalid or expired token' });
        }
        res.status(500).json({ error: 'Failed to reset password' });
    }
};

module.exports = { resetPassword };