import { auth, currentUser } from '@clerk/nextjs/server'
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

  // Get user information
  const user = await currentUser()

  // Return protected data
  return NextResponse.json({
    message: 'This route is now protected',
    userId: userId,
    userEmail: user?.emailAddresses[0]?.emailAddress,
    timestamp: new Date().toISOString(),
  })
}

// Example POST endpoint
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
      data: body,
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request body' },
      { status: 400 }
    )
  }
}

## Key Features Implemented:

### 1. **Middleware (middleware.ts)**
- Uses `clerkMiddleware()` from Clerk v5
- Defines protected routes using `createRouteMatcher()`
- Protects `/dashboard` and `/api/protected` routes
- Uses `auth.protect()` to enforce authentication
- Optimized matcher configuration to skip static files

### 2. **Dashboard Page (app/dashboard/page.tsx)**
- Server component with authentication check
- Uses `auth()` to get user ID
- Uses `currentUser()` to get full user details
- Displays user information
- Includes redirect as extra safety measure

### 3. **Protected API Route (app/api/protected/route.ts)**
- Checks authentication using `auth()`
- Returns 401 for unauthorized requests
- Includes both GET and POST examples
- Returns user context in responses

## Environment Variables Required:

Make sure you have these in your `.env.local`: