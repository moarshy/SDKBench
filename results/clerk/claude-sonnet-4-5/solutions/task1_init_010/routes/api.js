const express = require('express');
const { requireAuth } = require('@clerk/express');
const router = express.Router();

// Public API endpoint
router.get('/public', (req, res) => {
  res.json({
    message: 'This is a public API endpoint',
    timestamp: new Date().toISOString()
  });
});

// Protected API endpoint
router.get('/protected', requireAuth(), (req, res) => {
  const { userId, sessionId } = req.auth;
  
  res.json({
    message: 'This is a protected API endpoint',
    userId,
    sessionId,
    timestamp: new Date().toISOString()
  });
});

// API endpoint with custom auth check
router.post('/data', requireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    const data = req.body;
    
    // Your business logic here
    res.json({
      success: true,
      message: 'Data processed successfully',
      userId,
      data
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;

### 6. Clerk Helper Utilities