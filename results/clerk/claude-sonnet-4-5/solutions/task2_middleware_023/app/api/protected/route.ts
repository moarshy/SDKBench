import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the authentication state
  const { userId } = auth()

  // Return 401 if not authenticated
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
    timestamp: new Date().toISOString(),
  })
}

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from `@clerk/nextjs/server`
- Defined public routes using `createRouteMatcher` (home, sign-in, sign-up pages)
- Used `auth().protect()` to protect all non-public routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Imported `auth` and `currentUser` from `@clerk/nextjs/server`
- Added server-side authentication check using `auth()`
- Redirects to sign-in if user is not authenticated
- Displays user information when authenticated
- Made it an async server component to use Clerk's server helpers

### 3. **app/api/protected/route.ts**
- Imported `auth` from `@clerk/nextjs/server`
- Added authentication check at the API route level
- Returns 401 Unauthorized if user is not authenticated
- Returns protected data with userId when authenticated

## How It Works:

1. **Middleware Layer**: The middleware runs on every request and protects all routes except those defined in `isPublicRoute`
2. **Server Components**: The dashboard uses `auth()` to verify authentication server-side
3. **API Routes**: The protected API route checks authentication and returns appropriate responses

## Environment Variables Required:

Make sure you have these in your `.env.local`: