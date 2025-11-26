import { auth, currentUser } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the auth state
  const { userId } = await auth()

  // If no userId, return unauthorized
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }

  // Get the current user details
  const user = await currentUser()

  // Return protected data
  return NextResponse.json({
    message: 'This route is now protected',
    userId: userId,
    userEmail: user?.emailAddresses[0]?.emailAddress,
    timestamp: new Date().toISOString(),
  })
}

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from `@clerk/nextjs/server`
- Created route matchers to identify protected routes (`/dashboard`, `/api/protected`)
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async server component
- Added `auth()` to get the authentication state
- Added `currentUser()` to fetch user details
- Added a redirect to sign-in if user is not authenticated (backup check)
- Displays user information when authenticated

### 3. **app/api/protected/route.ts**
- Added `auth()` to check authentication status
- Returns 401 Unauthorized if no userId is present
- Fetches and returns user information in the response
- Properly handles the protected API route

## How It Works:

1. **Middleware Protection**: The middleware runs on every request and checks if the route is protected. If it is, it calls `auth.protect()` which will automatically redirect unauthenticated users to the sign-in page.

2. **Server-Side Checks**: Both the dashboard page and API route perform additional server-side checks using `auth()` to ensure the user is authenticated.

3. **User Data Access**: The code demonstrates how to access user information using `currentUser()` in both page components and API routes.

## Environment Variables Required:

Make sure you have these in your `.env.local`: