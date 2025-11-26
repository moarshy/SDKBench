I'll help you configure Clerk authentication middleware to protect your routes. Here's the complete solution:

```typescript
// filepath: middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define which routes should be protected
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/api/protected(.*)',
])

// Define public routes (optional - for explicit public routes)
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  // If the route is protected and user is not authenticated, redirect to sign-in
  if (isProtectedRoute(req)) {
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
  
  // If no userId, redirect to sign-in (extra safety check)
  if (!userId) {
    redirect('/sign-in')
  }

  // Get the current user details
  const user = await currentUser()

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <p className="mb-4">This page is now protected by Clerk authentication.</p>
      
      {user && (
        <div className="bg-gray-100 p-4 rounded-lg">
          <h2 className="text-xl font-semibold mb-2">User Information</h2>
          <p><strong>User ID:</strong> {user.id}</p>
          <p><strong>Email:</strong> {user.emailAddresses[0]?.emailAddress}</p>
          <p><strong>Name:</strong> {user.firstName} {user.lastName}</p>
        </div>
      )}
    </div>
  )
}
```

```typescript
// filepath: app/api/protected/route.ts
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

  // Get the current user details
  const user = await currentUser()

  // Return protected data
  return NextResponse.json({
    message: 'This is protected data',
    userId: userId,
    userEmail: user?.emailAddresses[0]?.emailAddress,
    timestamp: new Date().toISOString(),
  })
}

export async function POST() {
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }

  // Handle POST request with authentication
  return NextResponse.json({
    message: 'POST request successful',
    userId: userId,
  })
}
```

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from `@clerk/nextjs/server`
- Created route matchers to identify protected routes (`/dashboard`, `/api/protected`)
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async server component
- Added `auth()` to get the current user's authentication state
- Added `currentUser()` to fetch user details
- Added redirect logic for unauthenticated users (extra safety)
- Display user information when authenticated

### 3. **app/api/protected/route.ts**
- Added authentication checks using `auth()`
- Return 401 Unauthorized for unauthenticated requests
- Added user information to the response
- Included both GET and POST handlers as examples

## How It Works:

1. **Middleware Protection**: The middleware runs on every request and checks if the route is protected. If it is, it calls `auth.protect()` which will automatically redirect unauthenticated users to the sign-in page.

2. **Server-Side Auth**: Both the dashboard page and API route use server-side auth helpers to verify authentication and access user data.

3. **Route Matching**: The `createRouteMatcher` function creates efficient matchers for your protected routes, supporting wildcards with `(.*)`.

## Environment Variables Required:

Make sure you have these in your `.env.local`:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

The middleware will now protect your dashboard and API routes, automatically redirecting unauthenticated users to the Clerk sign-in page!