import { auth } from '@clerk/nextjs/server'

/**
 * Get the current user's ID or throw an error
 * Useful for API routes that require authentication
 */
export async function requireAuth() {
  const { userId } = await auth()
  
  if (!userId) {
    throw new Error('Unauthorized')
  }
  
  return userId
}

/**
 * Check if a user has a specific role
 */
export async function hasRole(role: string) {
  const { sessionClaims } = await auth()
  
  return sessionClaims?.metadata?.role === role
}

/**
 * Get user metadata
 */
export async function getUserMetadata() {
  const { sessionClaims } = await auth()
  
  return sessionClaims?.metadata || {}
}

## Key Features Implemented:

### 1. **Middleware Protection**
- Uses `clerkMiddleware()` from Clerk v5
- Protects all routes by default except those marked as public
- Uses `createRouteMatcher()` for clean route definitions

### 2. **Route Configuration**
- **Public routes**: Home, sign-in, sign-up, public APIs
- **Protected routes**: Dashboard, protected API routes
- **Ignored routes**: Health checks, status endpoints

### 3. **Server-Side Authentication**
- Dashboard page uses `auth()` and `currentUser()` helpers
- API routes check authentication status
- Proper error handling with 401 responses

### 4. **Client Components**
- Sign-in/up pages with Clerk components
- Home page with conditional rendering based on auth state

### 5. **Best Practices**
- Defense in depth (middleware + page-level checks)
- Proper TypeScript types
- Error handling
- Clean code organization
- Utility functions for common auth operations

## Testing the Implementation:

1. **Test protected routes**: Try accessing `/dashboard` without signing in
2. **Test API protection**: Call `/api/protected` without authentication
3. **Test public routes**: Access `/` and `/api/public` without signing in
4. **Test sign-in flow**: Sign in and verify redirect to dashboard

This solution provides enterprise-grade authentication with proper security, error handling, and user experience!