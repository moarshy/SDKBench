import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the authentication state
  const { userId } = await auth()
  
  // If no user is authenticated, return 401 Unauthorized
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
    timestamp: new Date().toISOString()
  })
}

// You can add other HTTP methods as needed
export async function POST(request: Request) {
  const { userId } = await auth()
  
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }
  
  // Handle POST request
  const body = await request.json()
  
  return NextResponse.json({ 
    message: 'Data received',
    userId: userId,
    data: body
  })
}

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from Clerk v5
- Created route matchers for protected routes (`/dashboard`, `/api/protected`)
- Created route matchers for public routes (sign-in, sign-up pages)
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to follow Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async server component
- Added `auth()` to check authentication status
- Added redirect to sign-in if user is not authenticated
- Used `currentUser()` to fetch and display user information
- Added user details display with proper null checking

### 3. **app/api/protected/route.ts**
- Added `auth()` check at the start of the route handler
- Returns 401 Unauthorized if no user is authenticated
- Returns protected data with userId when authenticated
- Added example POST handler showing the same pattern

## How It Works:

1. **Middleware Layer**: The middleware runs on every request matching the config pattern and checks if the route is protected
2. **Server-Side Protection**: Both the dashboard page and API route have additional server-side checks
3. **Automatic Redirects**: Unauthenticated users trying to access protected routes are automatically redirected to sign-in

## Environment Variables Required:

Make sure you have these in your `.env.local`: