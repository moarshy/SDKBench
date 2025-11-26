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
    message: 'This is protected data',
    userId: userId,
    userEmail: user?.emailAddresses[0]?.emailAddress,
    timestamp: new Date().toISOString(),
  })
}

export async function POST() {
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }

  // Handle POST request with authentication
  return NextResponse.json({
    message: 'POST request successful',
    userId: userId,
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
- Added `auth()` to get the current user's authentication state
- Added `currentUser()` to fetch user details
- Added redirect logic for unauthenticated users (extra safety)
- Display user information when authenticated

### 3. **app/api/protected/route.ts**
- Added authentication checks using `auth()`
- Return 401 Unauthorized for unauthenticated requests
- Added user information to the response
- Included both GET and POST handlers as examples

## How It Works:

1. **Middleware Protection**: The middleware runs on every request and checks if the route is protected. If it is, it calls `auth.protect()` which will automatically redirect unauthenticated users to the sign-in page.

2. **Server-Side Auth**: Both the dashboard page and API route use server-side auth helpers to verify authentication and access user data.

3. **Route Matching**: The `createRouteMatcher` function creates efficient matchers for your protected routes, supporting wildcards with `(.*)`.

## Environment Variables Required:

Make sure you have these in your `.env.local`: