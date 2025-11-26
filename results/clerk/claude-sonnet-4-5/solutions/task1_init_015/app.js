const express = require('express');
const { clerkMiddleware, requireAuth } = require('@clerk/express');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Initialize Clerk middleware
app.use(clerkMiddleware());

// Public routes
app.get('/', (req, res) => {
  res.json({ 
    message: 'Welcome to the API',
    authenticated: !!req.auth?.userId 
  });
});

app.get('/api/public', (req, res) => {
  res.json({ message: 'This is a public endpoint' });
});

// Protected routes - require authentication
app.get('/api/protected', requireAuth(), (req, res) => {
  res.json({ 
    message: 'This is a protected endpoint',
    userId: req.auth.userId,
    sessionId: req.auth.sessionId
  });
});

app.get('/api/user', requireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    res.json({ 
      message: 'User data retrieved successfully',
      userId: userId
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to retrieve user data' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Clerk authentication initialized`);
});

module.exports = app;