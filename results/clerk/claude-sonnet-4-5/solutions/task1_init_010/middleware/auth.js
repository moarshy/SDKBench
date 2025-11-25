const { clerkClient } = require('@clerk/express');
const { userHasRole } = require('../utils/clerkHelpers');

/**
 * Middleware to check if user has a specific role
 */
function requireRole(role) {
  return async (req, res, next) => {
    try {
      const { userId } = req.auth;
      
      if (!userId) {
        return res.status(401).json({
          error: {
            message: 'Unauthorized',
            status: 401
          }
        });
      }
      
      const hasRole = await userHasRole(userId, role);
      
      if (!hasRole) {
        return res.status(403).json({
          error: {
            message: 'Forbidden - Insufficient permissions',
            status: 403,
            requiredRole: role
          }
        });
      }
      
      next();
    } catch (error) {
      console.error('Error in requireRole middleware:', error);
      res.status(500).json({
        error: {
          message: 'Internal server error',
          status: 500
        }
      });
    }
  };
}

/**
 * Middleware to attach full user object to request
 */
async function attachUser(req, res, next) {
  try {
    const { userId } = req.auth;
    
    if (userId) {
      const user = await clerkClient.users.getUser(userId);
      req.user = user;
    }
    
    next();
  } catch (error) {
    console.error('Error attaching user:', error);
    next();
  }
}

/**
 * Optional auth - doesn't block if not authenticated
 */
function optionalAuth() {
  return (req, res, next) => {
    // Auth state is already available via clerkMiddleware
    // This is just a placeholder for additional logic if needed
    next();
  };
}

module.exports = {
  requireRole,
  attachUser,
  optionalAuth
};

### 8. Example HTML View (Sign-In)