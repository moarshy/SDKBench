I'll help you configure Clerk authentication middleware to protect your routes. Here's the complete solution:

```typescript
// filepath: middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define which routes should be protected
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/api/protected(.*)',
])

// Define public routes (optional - routes that should always be accessible)
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  // If the route is protected and not public, require authentication
  if (isProtectedRoute(req) && !isPublicRoute(req)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}
```

```typescript
// filepath: app/dashboard/page.tsx
import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function Dashboard() {
  // Get the auth state
  const { userId } = await auth()
  
  // If no user is signed in, redirect to sign-in page
  if (!userId) {
    redirect('/sign-in')
  }
  
  // Get the current user's details
  const user = await currentUser()

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <p className="mb-4">
        Welcome, {user?.firstName || user?.emailAddresses[0]?.emailAddress}!
      </p>
      <p className="text-green-600 font-semibold">
        ✓ This page is now protected by Clerk authentication
      </p>
      <div className="mt-6 p-4 bg-gray-100 rounded">
        <h2 className="font-semibold mb-2">User Information:</h2>
        <ul className="space-y-1">
          <li>User ID: {userId}</li>
          <li>Email: {user?.emailAddresses[0]?.emailAddress}</li>
          <li>Name: {user?.firstName} {user?.lastName}</li>
        </ul>
      </div>
    </div>
  )
}
```

```typescript
// filepath: app/api/protected/route.ts
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
```

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
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

## How It Works:

1. **Middleware runs first**: Checks if the route is protected
2. **Protected routes**: Require authentication via `auth.protect()`
3. **Public routes**: Bypass authentication checks
4. **Server components**: Can use `auth()` and `currentUser()` for additional checks
5. **API routes**: Can verify authentication and return appropriate responses

The solution is production-ready and follows Clerk v5 best practices!