import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the authentication state
  const { userId } = await auth()

  // If no userId, the user is not authenticated
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }

  // User is authenticated, return protected data
  return NextResponse.json({
    message: 'This is protected data',
    userId: userId,
    timestamp: new Date().toISOString(),
  })
}

// You can add other HTTP methods as needed
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

## Key Features Implemented:

### 1. **Middleware Configuration** (`middleware.ts`):
- Uses `clerkMiddleware()` from Clerk v5
- Defines protected routes using `createRouteMatcher()`
- Automatically protects `/dashboard` and `/api/protected` routes
- Uses `auth.protect()` to enforce authentication
- Optimized matcher pattern to exclude static files

### 2. **Protected Dashboard Page** (`app/dashboard/page.tsx`):
- Server component that checks authentication
- Uses `auth()` to get user ID
- Uses `currentUser()` to fetch user details
- Displays user information when authenticated
- Includes redirect as extra safety measure

### 3. **Protected API Route** (`app/api/protected/route.ts`):
- Checks authentication using `auth()`
- Returns 401 Unauthorized if not authenticated
- Returns protected data when authenticated
- Includes both GET and POST method examples

## How It Works:

1. **Middleware runs first** on every request matching the config
2. **Protected routes** require authentication via `auth.protect()`
3. **Unauthenticated users** are redirected to sign-in page
4. **Authenticated users** can access protected content
5. **API routes** return proper HTTP status codes

## Environment Variables Required:

Make sure you have these in your `.env.local`: