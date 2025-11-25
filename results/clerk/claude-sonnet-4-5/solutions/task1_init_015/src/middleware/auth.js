const { ClerkExpressRequireAuth } = require('@clerk/clerk-sdk-node');
const { clerkClient } = require('../config/clerk');

/**
 * Middleware to require authentication and attach full user object
 */
const requireAuthWithUser = () => {
  return [
    ClerkExpressRequireAuth(),
    async (req, res, next) => {
      try {
        const { userId } = req.auth;
        const user = await clerkClient.users.getUser(userId);
        req.user = user;
        next();
      } catch (error) {
        console.error('Error fetching user:', error);
        res.status(500).json({ error: 'Failed to fetch user information' });
      }
    }
  ];
};

/**
 * Middleware to check if user has specific role
 */
const requireRole = (role) => {
  return [
    ClerkExpressRequireAuth(),
    async (req, res, next) => {
      try {
        const { userId } = req.auth;
        const user = await clerkClient.users.getUser(userId);
        
        const userRole = user.publicMetadata?.role;
        
        if (userRole !== role) {
          return res.status(403).json({
            error: 'Forbidden',
            message: `This endpoint requires ${role} role`
          });
        }
        
        req.user = user;
        next();
      } catch (error) {
        console.error('Error checking role:', error);
        res.status(500).json({ error: 'Failed to verify user role' });
      }
    }
  ];
};

/**
 * Middleware to check if user has any of the specified roles
 */
const requireAnyRole = (roles) => {
  return [
    ClerkExpressRequireAuth(),
    async (req, res, next) => {
      try {
        const { userId } = req.auth;
        const user = await clerkClient.users.getUser(userId);
        
        const userRole = user.publicMetadata?.role;
        
        if (!roles.includes(userRole)) {
          return res.status(403).json({
            error: 'Forbidden',
            message: `This endpoint requires one of the following roles: ${roles.join(', ')}`
          });
        }
        
        req.user = user;
        next();
      } catch (error) {
        console.error('Error checking roles:', error);
        res.status(500).json({ error: 'Failed to verify user roles' });
      }
    }
  ];
};

module.exports = {
  requireAuthWithUser,
  requireRole,
  requireAnyRole
};

### 6. Example Routes with Custom Middleware