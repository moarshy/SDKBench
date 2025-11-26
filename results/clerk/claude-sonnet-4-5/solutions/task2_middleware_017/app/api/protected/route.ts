import { auth, currentUser } from '@clerk/nextjs/server'
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

  // Get the current user's information
  const user = await currentUser()

  // Return protected data
  return NextResponse.json({
    message: 'This is protected data',
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
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }

  return NextResponse.json({
    message: 'POST request successful',
    userId: userId,
  })
}

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from Clerk v5
- Created route matchers for protected routes (`/dashboard`, `/api/protected`)
- Created route matchers for public routes (sign-in, sign-up pages)
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async server component
- Added `auth()` to get the current user's authentication state
- Added `currentUser()` to fetch user details
- Added a redirect to sign-in if user is not authenticated (backup check)
- Displays user information when authenticated

### 3. **app/api/protected/route.ts**
- Added authentication check using `auth()`
- Returns 401 Unauthorized if user is not authenticated
- Fetches and returns user information in the response
- Added example POST method protection

## How It Works:

1. **Middleware Layer**: The middleware runs on every request matching the config pattern and checks if the route is protected
2. **Route Protection**: Protected routes require authentication via `auth.protect()`
3. **Server Components**: Use `auth()` and `currentUser()` for server-side authentication checks
4. **API Routes**: Check `userId` from `auth()` and return appropriate responses

## Environment Variables Required:

Make sure you have these in your `.env.local`: