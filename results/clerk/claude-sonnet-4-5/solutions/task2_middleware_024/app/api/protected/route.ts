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

  // Return protected data
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

  return NextResponse.json({
    message: 'POST request successful',
    userId: userId,
  })
}

## Key Features Implemented:

### 1. **Middleware Configuration** (`middleware.ts`):
- Uses `clerkMiddleware()` from Clerk v5
- Defines protected routes using `createRouteMatcher()`
- Protects `/dashboard` and `/api/protected` routes
- Uses `auth.protect()` to enforce authentication
- Optimized matcher configuration to skip static files

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
- Includes both GET and POST examples

## How It Works:

1. **Middleware runs first** on every request matching the config
2. **Protected routes** require authentication via `auth.protect()`
3. **Public routes** are accessible without authentication
4. **Dashboard page** displays user information after authentication
5. **API route** validates authentication and returns appropriate responses

## Environment Variables Required:

Make sure you have these in your `.env.local`: