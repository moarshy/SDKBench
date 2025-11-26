import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the auth state
  const { userId } = await auth()

  // Return 401 if not authenticated (extra safety check)
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized' },
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
- Created a route matcher to identify protected routes (`/dashboard` and `/api/protected`)
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async server component
- Added `auth()` to get the current user's authentication state
- Added `currentUser()` to fetch user details
- Added a redirect to sign-in page if user is not authenticated (extra safety)
- Displays user information when authenticated

### 3. **app/api/protected/route.ts**
- Added `auth()` from Clerk to check authentication
- Returns 401 Unauthorized if no userId is present (extra safety)
- Returns protected data including userId when authenticated

## How It Works:

1. **Middleware Protection**: The middleware runs on every request matching the config pattern. When a request hits a protected route, `auth.protect()` automatically redirects unauthenticated users to the sign-in page.

2. **Route Matching**: The `createRouteMatcher` function creates a matcher that checks if the current route should be protected. You can easily add more routes to the array.

3. **Server-Side Auth**: Both the dashboard page and API route use server-side auth helpers to verify authentication state, providing an additional layer of security.

## Environment Variables Required:

Make sure you have these in your `.env.local`: