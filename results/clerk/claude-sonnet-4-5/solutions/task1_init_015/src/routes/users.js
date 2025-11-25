const express = require('express');
const router = express.Router();
const { requireAuthWithUser, requireRole } = require('../middleware/auth');

// Get current user profile
router.get('/profile', requireAuthWithUser(), (req, res) => {
  res.json({
    user: {
      id: req.user.id,
      email: req.user.emailAddresses[0]?.emailAddress,
      firstName: req.user.firstName,
      lastName: req.user.lastName,
      imageUrl: req.user.imageUrl,
      role: req.user.publicMetadata?.role || 'user'
    }
  });
});

// Admin only endpoint
router.get('/admin/users', requireRole('admin'), async (req, res) => {
  try {
    const { clerkClient } = require('../config/clerk');
    const users = await clerkClient.users.getUserList();
    
    res.json({
      users: users.map(user => ({
        id: user.id,
        email: user.emailAddresses[0]?.emailAddress,
        firstName: user.firstName,
        lastName: user.lastName,
        createdAt: user.createdAt
      }))
    });
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

module.exports = router;

### 7. Package.json Scripts