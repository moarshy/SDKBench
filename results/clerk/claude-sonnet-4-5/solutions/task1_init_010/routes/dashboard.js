const express = require('express');
const { clerkClient } = require('@clerk/express');
const router = express.Router();

// All routes in this file are protected by requireAuth() middleware in app.js

router.get('/', async (req, res) => {
  try {
    const { userId } = req.auth;
    
    // Fetch user details from Clerk
    const user = await clerkClient.users.getUser(userId);
    
    res.json({
      message: 'Welcome to your dashboard',
      user: {
        id: user.id,
        email: user.emailAddresses[0]?.emailAddress,
        firstName: user.firstName,
        lastName: user.lastName,
        imageUrl: user.imageUrl,
        createdAt: user.createdAt
      }
    });
  } catch (error) {
    console.error('Error fetching user:', error);
    res.status(500).json({
      error: {
        message: 'Failed to fetch user data',
        details: error.message
      }
    });
  }
});

router.get('/profile', async (req, res) => {
  try {
    const { userId } = req.auth;
    const user = await clerkClient.users.getUser(userId);
    
    res.json({
      profile: {
        id: user.id,
        email: user.emailAddresses[0]?.emailAddress,
        firstName: user.firstName,
        lastName: user.lastName,
        username: user.username,
        imageUrl: user.imageUrl,
        phoneNumbers: user.phoneNumbers.map(phone => phone.phoneNumber),
        createdAt: user.createdAt,
        updatedAt: user.updatedAt
      }
    });
  } catch (error) {
    console.error('Error fetching profile:', error);
    res.status(500).json({
      error: {
        message: 'Failed to fetch profile',
        details: error.message
      }
    });
  }
});

module.exports = router;

### 5. API Routes