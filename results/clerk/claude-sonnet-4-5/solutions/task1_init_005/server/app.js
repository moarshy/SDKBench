const express = require('express');
const cors = require('cors');
const { clerkMiddleware, requireAuth } = require('@clerk/express');
require('dotenv').config();

const app = express();

// Middleware
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:5173',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Initialize Clerk middleware
app.use(clerkMiddleware());

// Public routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running' });
});

// Protected routes
app.get('/api/protected', requireAuth(), (req, res) => {
  const { userId, sessionId } = req.auth;
  res.json({ 
    message: 'Protected data',
    userId,
    sessionId
  });
});

app.get('/api/user/profile', requireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    res.json({ 
      userId,
      message: 'User profile data'
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch profile' });
  }
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error'
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;

### Frontend (React)