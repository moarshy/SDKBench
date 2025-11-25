const { requireAuth } = require('@clerk/express');

/**
 * Custom middleware to check if user is authenticated
 * and attach user data to request
 */
const authenticateUser = requireAuth();

/**
 * Optional middleware to check for specific roles or permissions
 */
const requireRole = (role) => {
  return async (req, res, next) => {
    try {
      const { userId } = req.auth;
      
      if (!userId) {
        return res.status(401).json({ error: 'Unauthorized' });
      }

      // You can fetch user metadata from Clerk here
      // and check for roles/permissions
      
      next();
    } catch (error) {
      res.status(500).json({ error: 'Authentication error' });
    }
  };
};

module.exports = {
  authenticateUser,
  requireRole
};

### 7. Package.json