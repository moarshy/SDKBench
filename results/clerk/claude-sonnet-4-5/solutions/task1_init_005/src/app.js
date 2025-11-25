require('dotenv').config();
const express = require('express');
const { clerkMiddleware, requireAuth } = require('@clerk/express');

const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Initialize Clerk middleware - this wraps your application
app.use(clerkMiddleware({
  publishableKey: process.env.CLERK_PUBLISHABLE_KEY,
  secretKey: process.env.CLERK_SECRET_KEY,
}));

// Serve static files (for frontend)
app.use(express.static('public'));

// Public routes (no authentication required)
app.get('/', (req, res) => {
  res.json({ 
    message: 'Welcome to the API',
    authenticated: !!req.auth?.userId 
  });
});

app.get('/api/public', (req, res) => {
  res.json({ message: 'This is a public endpoint' });
});

// Protected routes (authentication required)
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
    // You can fetch additional user data from Clerk if needed
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
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

module.exports = app;

### 3. Server Entry Point