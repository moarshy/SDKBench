import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the authentication state
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
    message: 'This route is now protected',
    userId: userId,
    timestamp: new Date().toISOString()
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
  
  // Handle POST request
  return NextResponse.json({ 
    message: 'POST request successful',
    userId: userId
  })
}

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from `@clerk/nextjs/server`
- Created route matchers to identify protected and public routes
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async server component
- Added `auth()` to get the user's authentication state
- Added `currentUser()` to fetch user details
- Added a redirect to sign-in page if user is not authenticated
- Displays user information when authenticated

### 3. **app/api/protected/route.ts**
- Added `auth()` from Clerk to check authentication
- Returns 401 Unauthorized if user is not authenticated
- Returns protected data with userId when authenticated
- Added example POST handler showing the same pattern

## How It Works:

1. **Middleware Layer**: The middleware runs on every request matching the config pattern and protects routes using `auth.protect()`
2. **Route Protection**: Routes matching `/dashboard(.*)` and `/api/protected(.*)` require authentication
3. **Public Routes**: Routes like `/`, `/sign-in`, and `/sign-up` remain accessible
4. **Server-Side Checks**: Additional auth checks in components and API routes provide defense in depth

## Environment Variables Required:

Make sure you have these in your `.env.local`: