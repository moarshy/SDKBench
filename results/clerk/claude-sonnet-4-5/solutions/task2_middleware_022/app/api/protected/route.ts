import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the auth state
  const { userId } = await auth()

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
    message: 'Protected POST endpoint',
    userId: userId,
  })
}

## Key Features Implemented:

### 1. **Middleware Configuration** (`middleware.ts`):
   - Uses `clerkMiddleware()` from Clerk v5
   - Defines protected routes using `createRouteMatcher()`
   - Protects `/dashboard` and `/api/protected` routes
   - Allows public access to sign-in/sign-up pages
   - Uses `auth.protect()` to enforce authentication

### 2. **Protected Dashboard Page** (`app/dashboard/page.tsx`):
   - Server component that checks authentication
   - Uses `auth()` to get user ID
   - Uses `currentUser()` to fetch user details
   - Displays user information when authenticated
   - Redirects to sign-in if not authenticated (extra safety)

### 3. **Protected API Route** (`app/api/protected/route.ts`):
   - Checks authentication using `auth()`
   - Returns 401 for unauthenticated requests
   - Includes both GET and POST handlers
   - Returns user-specific data when authenticated

## How It Works:

1. **Middleware runs first** on every request matching the config
2. **Protected routes** require authentication via `auth.protect()`
3. **Unauthenticated users** are redirected to sign-in
4. **Server components and API routes** have additional auth checks
5. **Public routes** remain accessible to everyone

## Environment Variables Required:

Make sure you have these in your `.env.local`: