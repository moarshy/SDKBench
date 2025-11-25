import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignUp />
    </div>
  )
}

## Key Features Implemented:

### 1. **Middleware Protection**
- Uses `clerkMiddleware()` from Clerk v5
- Protects all routes by default except those matched by `isPublicRoute`
- Proper matcher configuration to exclude static files

### 2. **Public Routes**
- Home page (`/`)
- Sign-in and sign-up pages
- Public API routes
- Webhook routes

### 3. **Protected Routes**
- Dashboard page with user information
- Protected API routes with proper error handling
- Automatic redirect for unauthenticated users

### 4. **Server-Side Auth**
- Uses `auth()` for getting authentication state
- Uses `currentUser()` for getting full user details
- Proper error handling in API routes

### 5. **Client Components**
- `SignInButton`, `SignUpButton`, and `UserButton` for UI
- Modal-based authentication flow

## Testing the Implementation:

1. **Test Public Access**: Visit `/` - should work without auth
2. **Test Protected Page**: Visit `/dashboard` - should redirect to sign-in
3. **Test Protected API**: Call `/api/protected` - should return 401
4. **Test Public API**: Call `/api/public` - should work without auth
5. **Test After Sign-In**: Sign in and access dashboard - should show user info

This implementation follows Clerk v5 best practices and provides a secure, production-ready authentication system!