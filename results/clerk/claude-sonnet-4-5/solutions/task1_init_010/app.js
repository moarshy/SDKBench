const express = require('express');
const { ClerkExpressRequireAuth, ClerkExpressWithAuth } = require('@clerk/clerk-sdk-node');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Public routes (no authentication required)
app.get('/', (req, res) => {
  res.json({ 
    message: 'Welcome to the API',
    status: 'public'
  });
});

app.get('/api/public', (req, res) => {
  res.json({ 
    message: 'This is a public endpoint',
    timestamp: new Date().toISOString()
  });
});

// Protected routes (authentication required)
app.get('/api/protected', ClerkExpressRequireAuth(), (req, res) => {
  const { userId, sessionId } = req.auth;
  res.json({ 
    message: 'This is a protected endpoint',
    userId,
    sessionId,
    timestamp: new Date().toISOString()
  });
});

// Optional authentication (user data available if authenticated)
app.get('/api/optional', ClerkExpressWithAuth(), (req, res) => {
  const { userId } = req.auth;
  
  if (userId) {
    res.json({ 
      message: 'You are authenticated',
      userId,
      timestamp: new Date().toISOString()
    });
  } else {
    res.json({ 
      message: 'You are not authenticated, but that\'s okay',
      timestamp: new Date().toISOString()
    });
  }
});

// Get current user information
app.get('/api/me', ClerkExpressRequireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    const { clerkClient } = require('@clerk/clerk-sdk-node');
    
    const user = await clerkClient.users.getUser(userId);
    
    res.json({
      id: user.id,
      email: user.emailAddresses[0]?.emailAddress,
      firstName: user.firstName,
      lastName: user.lastName,
      username: user.username,
      imageUrl: user.imageUrl
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to fetch user data',
      message: error.message 
    });
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
    error: 'Internal Server Error',
    message: err.message 
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ 
    error: 'Not Found',
    message: 'The requested resource does not exist'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`Clerk configured: ${!!process.env.CLERK_SECRET_KEY}`);
});

module.exports = app;