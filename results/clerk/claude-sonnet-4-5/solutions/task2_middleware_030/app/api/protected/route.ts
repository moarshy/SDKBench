import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the authentication state
  const { userId } = await auth()

  // Check if user is authenticated
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

  // Handle POST request with authenticated user
  return NextResponse.json({
    message: 'POST request successful',
    userId: userId,
  })
}

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from `@clerk/nextjs/server`
- Created route matchers to identify protected routes (`/dashboard`, `/api/protected`)
- Added optional public route matcher for clarity
- Used `auth.protect()` to enforce authentication on protected routes
- Updated matcher config to follow Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async Server Component
- Added `auth()` to get authentication state
- Added `currentUser()` to fetch user details
- Added redirect for unauthenticated users (defense in depth)
- Display user information when authenticated

### 3. **app/api/protected/route.ts**
- Added `auth()` to check authentication state
- Return 401 Unauthorized if user is not authenticated
- Added both GET and POST handlers as examples
- Return user ID in response for verification

## How It Works:

1. **Middleware Layer**: The middleware runs on every request matching the config pattern and protects routes before they're accessed
2. **Server Component**: The dashboard page uses server-side auth helpers to verify authentication
3. **API Routes**: Protected API routes check authentication and return appropriate responses

## Testing:

1. Try accessing `/dashboard` without signing in → redirected to sign-in
2. Try accessing `/api/protected` without auth → 401 Unauthorized
3. Sign in and access both → should work correctly

Make sure you have these environment variables set:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`