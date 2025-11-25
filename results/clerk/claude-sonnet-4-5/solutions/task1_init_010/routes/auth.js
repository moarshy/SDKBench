const express = require('express');
const { ClerkExpressRequireAuth } = require('@clerk/clerk-sdk-node');
const { clerkClient } = require('@clerk/clerk-sdk-node');
const router = express.Router();

// Get current user
router.get('/me', ClerkExpressRequireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    const user = await clerkClient.users.getUser(userId);
    
    res.json({
      id: user.id,
      email: user.emailAddresses[0]?.emailAddress,
      firstName: user.firstName,
      lastName: user.lastName,
      username: user.username,
      imageUrl: user.imageUrl,
      createdAt: user.createdAt,
      updatedAt: user.updatedAt
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to fetch user data',
      message: error.message 
    });
  }
});

// Update user metadata
router.patch('/me', ClerkExpressRequireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    const { publicMetadata, privateMetadata } = req.body;
    
    const user = await clerkClient.users.updateUser(userId, {
      publicMetadata,
      privateMetadata
    });
    
    res.json({
      message: 'User updated successfully',
      user: {
        id: user.id,
        publicMetadata: user.publicMetadata,
        updatedAt: user.updatedAt
      }
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to update user',
      message: error.message 
    });
  }
});

// Get user sessions
router.get('/sessions', ClerkExpressRequireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    const sessions = await clerkClient.users.getUserList({ userId });
    
    res.json({
      sessions: sessions.map(session => ({
        id: session.id,
        status: session.status,
        lastActiveAt: session.lastActiveAt,
        expireAt: session.expireAt
      }))
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to fetch sessions',
      message: error.message 
    });
  }
});

module.exports = router;

This complete solution provides:

1. **Express app with Clerk integration** - Full authentication setup
2. **Multiple endpoint types** - Public, protected, and optional auth
3. **User management** - Get and update user data
4. **Error handling** - Comprehensive error middleware
5. **Environment configuration** - Proper setup with .env
6. **Documentation** - Complete README with examples
7. **Modular structure** - Separate routes and middleware

To use this:
1. Run `npm install` to install dependencies
2. Copy `.env.example` to `.env` and add your Clerk keys
3. Run `npm run dev` to start the server
4. Test endpoints with curl or integrate with a frontend