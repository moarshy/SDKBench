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
- Created route matchers for protected and public routes
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async Server Component
- Added `auth()` to check authentication status
- Added `currentUser()` to fetch user details
- Added redirect logic for unauthenticated users
- Displays user information when authenticated

### 3. **app/api/protected/route.ts**
- Added `auth()` check at the beginning of the handler
- Returns 401 Unauthorized if no user is authenticated
- Returns protected data with userId when authenticated
- Added example POST handler showing the same pattern

## How It Works:

1. **Middleware Layer**: The middleware runs on every request matching the config pattern and protects routes defined in `isProtectedRoute`
2. **Server Components**: Use `auth()` and `currentUser()` for server-side authentication checks
3. **API Routes**: Use `auth()` to verify authentication and return appropriate responses

## Environment Variables Required:

Make sure you have these in your `.env.local`: