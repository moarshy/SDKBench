const express = require('express');
const router = express.Router();

// Home page - accessible to everyone
router.get('/', (req, res) => {
  const { userId, sessionId } = req.auth;
  
  res.json({
    message: 'Welcome to the application',
    authenticated: !!userId,
    userId: userId || null,
    sessionId: sessionId || null
  });
});

// Sign-in page route (if serving HTML)
router.get('/sign-in', (req, res) => {
  res.render('sign-in', {
    publishableKey: process.env.CLERK_PUBLISHABLE_KEY
  });
});

// Sign-up page route (if serving HTML)
router.get('/sign-up', (req, res) => {
  res.render('sign-up', {
    publishableKey: process.env.CLERK_PUBLISHABLE_KEY
  });
});

module.exports = router;

### 4. Protected Routes (Dashboard)