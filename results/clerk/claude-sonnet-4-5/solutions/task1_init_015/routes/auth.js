const express = require('express');
const { requireAuth } = require('@clerk/express');
const router = express.Router();

// Get current user session info
router.get('/session', requireAuth(), (req, res) => {
  res.json({
    userId: req.auth.userId,
    sessionId: req.auth.sessionId,
    orgId: req.auth.orgId,
    orgRole: req.auth.orgRole,
    orgSlug: req.auth.orgSlug
  });
});

// Webhook endpoint for Clerk events (optional)
router.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  // Verify webhook signature and process events
  // See: https://clerk.com/docs/integrations/webhooks
  
  try {
    // Process webhook event
    const event = req.body;
    
    console.log('Received webhook event:', event.type);
    
    res.status(200).json({ received: true });
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(400).json({ error: 'Webhook processing failed' });
  }
});

module.exports = router;