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
  
  // Get the current user's information
  const user = await currentUser()
  
  // Return protected data
  return NextResponse.json({
    message: 'This route is now protected',
    userId: userId,
    userEmail: user?.emailAddresses[0]?.emailAddress,
    timestamp: new Date().toISOString(),
  })
}

// You can also protect other HTTP methods
export async function POST() {
  const { userId } = await auth()
  
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }
  
  // Handle POST request for authenticated users
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
   - Optimized matcher pattern to skip static files

### 2. **Protected Dashboard Page** (`app/dashboard/page.tsx`):
   - Server component with authentication check
   - Uses `auth()` to get user ID
   - Uses `currentUser()` to fetch user details
   - Displays user information when authenticated
   - Includes redirect as extra safety measure

### 3. **Protected API Route** (`app/api/protected/route.ts`):
   - Checks authentication status
   - Returns 401 for unauthorized requests
   - Provides user data in response
   - Supports multiple HTTP methods

## Environment Variables Required:

Make sure you have these in your `.env.local`: