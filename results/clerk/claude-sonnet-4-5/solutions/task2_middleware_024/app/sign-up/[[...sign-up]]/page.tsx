import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <SignUp />
    </div>
  )
}

## Key Features Implemented:

### 1. **Middleware Protection**
- Uses `clerkMiddleware()` from Clerk v5
- Protects all routes by default except those marked as public
- Uses `createRouteMatcher()` for efficient route matching

### 2. **Route Configuration**
- **Public routes**: Home, sign-in, sign-up, webhooks
- **Protected routes**: Dashboard, protected API routes
- **Ignored routes**: Health checks and status endpoints

### 3. **Server-Side Authentication**
- Dashboard uses `auth()` to get user ID
- Protected API route validates authentication
- Proper error handling with 401 responses

### 4. **Client Components**
- Sign-in/Sign-up buttons with modal mode
- UserButton for authenticated users
- Proper navigation between protected and public routes

## Testing the Implementation:

1. **Test Public Access**: Visit `/` - should work without authentication
2. **Test Protected Route**: Visit `/dashboard` - should redirect to sign-in
3. **Test Protected API**: Call `/api/protected` - should return 401 if not authenticated
4. **Test Public API**: Call `/api/public` - should work without authentication
5. **Test After Sign-In**: Sign in and visit `/dashboard` - should show user info

## Additional Security Notes:

- Middleware runs on every request matching the config
- `auth().protect()` automatically redirects unauthenticated users
- Server-side auth checks provide defense in depth
- API routes have explicit authentication checks

This setup provides comprehensive protection for your Next.js application using Clerk v5!