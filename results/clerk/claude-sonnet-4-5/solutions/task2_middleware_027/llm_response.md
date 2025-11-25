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
    message: 'This route is now protected by Clerk authentication',
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
```

## Key Features Implemented:

### 1. **Middleware Configuration** (`middleware.ts`):
   - Uses `clerkMiddleware()` from Clerk v5
   - Defines protected routes using `createRouteMatcher()`
   - Automatically protects `/dashboard` and `/api/protected` routes
   - Uses `auth.protect()` to enforce authentication
   - Optimized matcher pattern to exclude static files

### 2. **Protected Dashboard Page** (`app/dashboard/page.tsx`):
   - Server component that checks authentication
   - Uses `auth()` to get user ID
   - Uses `currentUser()` to get full user details
   - Redirects unauthenticated users to sign-in
   - Displays user information when authenticated

### 3. **Protected API Route** (`app/api/protected/route.ts`):
   - Checks authentication using `auth()`
   - Returns 401 for unauthenticated requests
   - Returns protected data for authenticated users
   - Includes examples for both GET and POST methods

## How It Works:

1. **Middleware runs first** on every request matching the config
2. **Protected routes** require authentication via `auth.protect()`
3. **Dashboard page** double-checks auth and redirects if needed
4. **API route** validates auth and returns appropriate responses

## Environment Variables Required:

Make sure you have these in your `.env.local`:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

The solution is production-ready and follows Clerk v5 best practices!