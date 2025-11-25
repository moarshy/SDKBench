import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the authentication state
  const { userId } = await auth()

  // If no user is authenticated, return 401 Unauthorized
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in to access this resource' },
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

// You can also add other HTTP methods
export async function POST(request: Request) {
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  try {
    const body = await request.json()
    
    // Process the request with authenticated user
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

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from Clerk v5
- Created route matchers for protected routes (`/dashboard`, `/api/protected`)
- Added optional public routes matcher for clarity
- Used `auth.protect()` to enforce authentication on protected routes
- Updated matcher config to follow Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to async server component
- Added `auth()` to check authentication status
- Added `currentUser()` to fetch user details
- Added redirect logic for unauthenticated users
- Displays user information when authenticated

### 3. **app/api/protected/route.ts**
- Added `auth()` check at the start of the handler
- Returns 401 Unauthorized if no userId is present
- Added example POST handler showing the same pattern
- Includes proper error handling

## How It Works:

1. **Middleware Layer**: The middleware runs on every request matching the config pattern and protects specified routes
2. **Server Components**: Use `auth()` and `currentUser()` for server-side authentication checks
3. **API Routes**: Use `auth()` to verify authentication and return appropriate responses

## Environment Variables Required:

Make sure you have these in your `.env.local`: