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
  
  // Return protected data
  return NextResponse.json({ 
    message: 'This route is now protected!',
    userId: userId,
    timestamp: new Date().toISOString()
  })
}

## What Changed:

### middleware.ts
1. **Imported Clerk v5 middleware**: Using `clerkMiddleware` and `createRouteMatcher` from `@clerk/nextjs/server`
2. **Defined protected routes**: Dashboard and protected API routes require authentication
3. **Defined public routes**: Sign-in, sign-up, and home page remain accessible
4. **Added auth protection**: Routes matching the protected pattern will call `auth.protect()` to enforce authentication
5. **Updated matcher config**: Using the recommended Clerk v5 matcher pattern

### app/dashboard/page.tsx
1. **Added server-side auth check**: Using `auth()` to get the user ID
2. **Added redirect logic**: Redirects unauthenticated users to sign-in
3. **Fetched user data**: Using `currentUser()` to display user information
4. **Enhanced UI**: Shows welcome message and user details

### app/api/protected/route.ts
1. **Added auth check**: Verifies user is authenticated before processing request
2. **Returns 401 for unauthorized**: Proper HTTP status code for unauthenticated requests
3. **Returns user data**: Includes userId in the response for authenticated users

## Environment Variables Needed:

Make sure you have these in your `.env.local`: