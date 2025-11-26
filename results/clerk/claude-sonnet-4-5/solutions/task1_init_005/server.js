const express = require('express');
const { clerkMiddleware, requireAuth } = require('@clerk/express');
const cors = require('cors');
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

// Protected routes example
app.get('/api/protected', requireAuth(), (req, res) => {
  const { userId } = req.auth;
  res.json({ 
    message: 'This is a protected route',
    userId 
  });
});

// User info route
app.get('/api/user', requireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    res.json({ 
      userId,
      message: 'User authenticated successfully'
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch user data' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;