const { clerkClient } = require('@clerk/clerk-sdk-node');

// Validate Clerk configuration
const validateClerkConfig = () => {
  if (!process.env.CLERK_PUBLISHABLE_KEY) {
    throw new Error('CLERK_PUBLISHABLE_KEY is not set in environment variables');
  }
  
  if (!process.env.CLERK_SECRET_KEY) {
    throw new Error('CLERK_SECRET_KEY is not set in environment variables');
  }
  
  console.log('✅ Clerk configuration validated');
};

// Initialize Clerk
const initializeClerk = () => {
  try {
    validateClerkConfig();
    return clerkClient;
  } catch (error) {
    console.error('❌ Clerk initialization failed:', error.message);
    process.exit(1);
  }
};

module.exports = {
  clerkClient: initializeClerk(),
  validateClerkConfig
};

### 5. Custom Middleware for Enhanced Auth