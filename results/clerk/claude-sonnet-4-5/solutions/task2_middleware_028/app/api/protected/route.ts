import { auth } from '@clerk/nextjs/server'
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

  // Return protected data
  return NextResponse.json({
    message: 'This is protected data',
    userId: userId,
    timestamp: new Date().toISOString(),
    data: {
      secretInfo: 'Only authenticated users can see this',
      userSpecific: `Data for user ${userId}`,
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

### 1. **Middleware (middleware.ts)**:
- Uses `clerkMiddleware()` from Clerk v5
- Defines protected routes using `createRouteMatcher()`
- Automatically protects `/dashboard` and `/api/protected` routes
- Uses `auth.protect()` to enforce authentication
- Optimized matcher config to skip static files

### 2. **Dashboard Page (app/dashboard/page.tsx)**:
- Server component that uses `auth()` and `currentUser()`
- Displays user information
- Has backup redirect if somehow accessed without auth
- Shows personalized welcome message

### 3. **Protected API Route (app/api/protected/route.ts)**:
- Checks authentication using `auth()`
- Returns 401 for unauthorized requests
- Includes both GET and POST methods as examples
- Returns user-specific data when authenticated

## Environment Variables Required:

Make sure you have these in your `.env.local`: