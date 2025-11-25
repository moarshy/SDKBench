const { clerkClient } = require('@clerk/express');

/**
 * Get user by ID
 */
async function getUserById(userId) {
  try {
    const user = await clerkClient.users.getUser(userId);
    return user;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}

/**
 * Update user metadata
 */
async function updateUserMetadata(userId, metadata) {
  try {
    const user = await clerkClient.users.updateUserMetadata(userId, {
      publicMetadata: metadata
    });
    return user;
  } catch (error) {
    console.error('Error updating user metadata:', error);
    throw error;
  }
}

/**
 * Get all sessions for a user
 */
async function getUserSessions(userId) {
  try {
    const sessions = await clerkClient.sessions.getSessionList({
      userId
    });
    return sessions;
  } catch (error) {
    console.error('Error fetching sessions:', error);
    throw error;
  }
}

/**
 * Revoke a session
 */
async function revokeSession(sessionId) {
  try {
    const session = await clerkClient.sessions.revokeSession(sessionId);
    return session;
  } catch (error) {
    console.error('Error revoking session:', error);
    throw error;
  }
}

/**
 * Check if user has specific role (using public metadata)
 */
async function userHasRole(userId, role) {
  try {
    const user = await getUserById(userId);
    const roles = user.publicMetadata?.roles || [];
    return roles.includes(role);
  } catch (error) {
    console.error('Error checking user role:', error);
    return false;
  }
}

module.exports = {
  getUserById,
  updateUserMetadata,
  getUserSessions,
  revokeSession,
  userHasRole
};

### 7. Custom Middleware