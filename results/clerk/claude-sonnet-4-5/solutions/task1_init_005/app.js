const express = require('express');
const { clerkMiddleware, requireAuth } = require('@clerk/express');
require('dotenv').config();

const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Initialize Clerk middleware
app.use(clerkMiddleware());

// Public routes
app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API' });
});

app.get('/api/public', (req, res) => {
  res.json({ message: 'This is a public endpoint' });
});

// Protected routes - require authentication
app.get('/api/protected', requireAuth(), (req, res) => {
  const { userId, sessionId } = req.auth;
  res.json({ 
    message: 'This is a protected endpoint',
    userId,
    sessionId
  });
});

app.get('/api/user', requireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    res.json({ 
      message: 'User data',
      userId,
      // You can fetch additional user data from Clerk here
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch user data' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error'
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

module.exports = app;