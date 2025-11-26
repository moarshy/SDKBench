import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the auth state
  const { userId } = await auth()
  
  // If no user is authenticated, return 401 Unauthorized
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }
  
  // Return protected data
  return NextResponse.json({ 
    message: 'This route is now protected',
    userId: userId,
    timestamp: new Date().toISOString()
  })
}

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from `@clerk/nextjs/server`
- Created route matchers to identify protected and public routes
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Imported `auth` and `currentUser` from `@clerk/nextjs/server`
- Added server-side authentication check
- Redirects unauthenticated users to sign-in page
- Displays user information when authenticated

### 3. **app/api/protected/route.ts**
- Imported `auth` from `@clerk/nextjs/server`
- Added authentication check at the API route level
- Returns 401 status for unauthenticated requests
- Returns protected data with user ID for authenticated requests

## How It Works:

1. **Middleware Layer**: The middleware runs on every request matching the config pattern and protects routes defined in `isProtectedRoute`
2. **Server Components**: The dashboard page uses `auth()` to check authentication status server-side
3. **API Routes**: The protected API route validates authentication before returning data

## Environment Variables Required:

Make sure you have these in your `.env.local`: