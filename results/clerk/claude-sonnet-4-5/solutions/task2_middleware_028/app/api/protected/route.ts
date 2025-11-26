import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the auth state
  const { userId } = await auth()
  
  // If no user is authenticated, return 401
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

// You can also protect other HTTP methods
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
    userId: userId
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
- Server component that checks authentication
- Uses `auth()` to get user ID
- Uses `currentUser()` to get full user details
- Redirects unauthenticated users to sign-in
- Displays user information

### 3. **Protected API Route** (`app/api/protected/route.ts`):
- Checks authentication using `auth()`
- Returns 401 for unauthenticated requests
- Includes userId in response for authenticated users
- Supports multiple HTTP methods (GET, POST)

## How It Works:

1. **Middleware Layer**: Runs on every request matching the config pattern
2. **Route Protection**: Automatically redirects unauthenticated users trying to access protected routes
3. **Server-Side Auth**: Both page and API route verify authentication server-side
4. **Type Safety**: Full TypeScript support with proper types

## Environment Variables Required:

Make sure you have these in your `.env.local`: