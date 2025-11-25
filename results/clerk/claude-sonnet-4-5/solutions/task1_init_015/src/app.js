require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { ClerkExpressRequireAuth, ClerkExpressWithAuth } = require('@clerk/clerk-sdk-node');

const app = express();

// Middleware
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint (public)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running' });
});

// Public routes
app.get('/api/public', (req, res) => {
  res.json({ message: 'This is a public endpoint' });
});

// Protected route - requires authentication
app.get('/api/protected', ClerkExpressRequireAuth(), (req, res) => {
  const { userId, sessionId } = req.auth;
  res.json({
    message: 'This is a protected endpoint',
    userId,
    sessionId
  });
});

// Optional authentication - works with or without auth
app.get('/api/optional', ClerkExpressWithAuth(), (req, res) => {
  const { userId } = req.auth;
  
  if (userId) {
    res.json({
      message: 'You are authenticated',
      userId
    });
  } else {
    res.json({
      message: 'You are not authenticated, but that\'s okay'
    });
  }
});

// Get current user information
app.get('/api/user', ClerkExpressRequireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    const { clerkClient } = require('@clerk/clerk-sdk-node');
    
    const user = await clerkClient.users.getUser(userId);
    
    res.json({
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
    res.status(500).json({ error: 'Failed to fetch user information' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  
  // Clerk authentication errors
  if (err.status === 401) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Authentication required'
    });
  }
  
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

module.exports = app;

### 3. Server Entry Point