const express = require('express');
const cors = require('cors');
const { clerkMiddleware, requireAuth, getAuth } = require('@clerk/express');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());

// Initialize Clerk middleware
app.use(clerkMiddleware());

// Public routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running' });
});

// Protected routes - require authentication
app.get('/api/protected', requireAuth(), (req, res) => {
  const { userId, sessionId } = getAuth(req);
  res.json({ 
    message: 'This is a protected route',
    userId,
    sessionId
  });
});

// Get current user info
app.get('/api/user', requireAuth(), async (req, res) => {
  try {
    const { userId } = getAuth(req);
    res.json({ 
      userId,
      message: 'User authenticated successfully'
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get user info' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error'
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;