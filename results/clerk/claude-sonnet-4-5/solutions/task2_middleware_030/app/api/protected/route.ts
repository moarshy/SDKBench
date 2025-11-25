import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the auth state
  const { userId } = await auth()
  
  // If no user is authenticated, return 401 Unauthorized
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

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from `@clerk/nextjs/server`
- Created route matchers for protected routes (`/dashboard`, `/api/protected`)
- Created route matchers for public routes (sign-in, sign-up pages)
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Imported `auth` and `currentUser` from `@clerk/nextjs/server`
- Added server-side authentication check using `auth()`
- Added redirect to sign-in page if user is not authenticated
- Displayed user information from `currentUser()`
- Made it a server component (async function)

### 3. **app/api/protected/route.ts**
- Imported `auth` from `@clerk/nextjs/server`
- Added authentication check at the API route level
- Returns 401 Unauthorized if no user is authenticated
- Returns protected data with userId when authenticated

## How It Works:

1. **Middleware Layer**: The middleware runs on every request matching the config pattern and checks if the route is protected
2. **Route Protection**: Protected routes require authentication via `auth.protect()`
3. **Server Components**: Dashboard page checks auth state server-side
4. **API Routes**: Protected API routes verify authentication before returning data

## Environment Variables Required:

Make sure you have these in your `.env.local`: