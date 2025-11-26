const { requireAuth } = require('@clerk/express');

/**
 * Custom authentication middleware with additional checks
 */
const authenticateUser = () => {
  return [
    requireAuth(),
    (req, res, next) => {
      // Additional custom validation can be added here
      if (!req.auth?.userId) {
        return res.status(401).json({ 
          error: 'Unauthorized',
          message: 'Valid authentication required' 
        });
      }
      next();
    }
  ];
};

/**
 * Optional: Role-based access control middleware
 */
const requireRole = (role) => {
  return async (req, res, next) => {
    try {
      const { userId } = req.auth;
      
      // You would typically fetch user metadata from Clerk here
      // const user = await clerkClient.users.getUser(userId);
      // const userRole = user.publicMetadata?.role;
      
      // For now, this is a placeholder
      // Implement your role checking logic based on your needs
      
      next();
    } catch (error) {
      res.status(403).json({ 
        error: 'Forbidden',
        message: 'Insufficient permissions' 
      });
    }
  };
};

module.exports = {
  authenticateUser,
  requireRole
};