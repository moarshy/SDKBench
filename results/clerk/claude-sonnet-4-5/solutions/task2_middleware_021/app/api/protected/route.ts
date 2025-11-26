import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the authentication state
  const { userId } = await auth()

  // If no userId, return unauthorized
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }

  // Return protected data
  return NextResponse.json({
    message: 'This route is now protected!',
    userId: userId,
    timestamp: new Date().toISOString(),
    data: {
      secret: 'This is sensitive information only for authenticated users',
    },
  })
}

// You can also add other HTTP methods
export async function POST(request: Request) {
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }

  try {
    const body = await request.json()
    
    // Process the request with authenticated user context
    return NextResponse.json({
      message: 'Data processed successfully',
      userId: userId,
      receivedData: body,
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request body' },
      { status: 400 }
    )
  }
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
   - Displays personalized welcome message
   - Shows user information safely

### 3. **Protected API Route** (`app/api/protected/route.ts`):
   - Checks authentication using `auth()`
   - Returns 401 for unauthenticated requests
   - Includes both GET and POST handlers
   - Returns user-specific data when authenticated

## How It Works:

1. **Middleware runs first** on every request matching the config
2. **Protected routes** require authentication via `auth.protect()`
3. **Unauthenticated users** are redirected to sign-in
4. **Authenticated users** can access protected content
5. **API routes** have additional server-side checks for security

## Environment Variables Required:

Make sure you have these in your `.env.local`: