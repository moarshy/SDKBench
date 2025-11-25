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
    message: 'This is protected data',
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
- Converted to an async server component
- Added `auth()` to check authentication status
- Added `currentUser()` to fetch user details
- Added redirect logic for unauthenticated users
- Displays user information when authenticated

### 3. **app/api/protected/route.ts**
- Added `auth()` to verify authentication
- Returns 401 status for unauthenticated requests
- Returns protected data with user ID for authenticated requests

## How It Works:

1. **Middleware Protection**: The middleware runs on every request and checks if the route is protected
2. **Route Matching**: Uses `createRouteMatcher` to define which routes require authentication
3. **Authentication Check**: `auth.protect()` ensures users are signed in before accessing protected routes
4. **Server-Side Validation**: Both the page and API route verify authentication server-side

## Environment Variables Required:

Make sure you have these in your `.env.local`: