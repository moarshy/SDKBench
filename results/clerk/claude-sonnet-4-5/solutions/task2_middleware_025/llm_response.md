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
        This page is now protected by Clerk authentication.
      </p>
      {user && (
        <div className="bg-gray-100 p-4 rounded-lg">
          <h2 className="text-xl font-semibold mb-2">User Information</h2>
          <p><strong>User ID:</strong> {user.id}</p>
          <p><strong>Email:</strong> {user.emailAddresses[0]?.emailAddress}</p>
          <p>
            <strong>Name:</strong> {user.firstName} {user.lastName}
          </p>
        </div>
      )}
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
  
  // User is authenticated, return protected data
  return NextResponse.json({ 
    message: 'This is protected data',
    userId: userId,
    timestamp: new Date().toISOString()
  })
}

// You can add other HTTP methods as needed
export async function POST(request: Request) {
  const { userId } = await auth()
  
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }
  
  // Handle POST request
  const body = await request.json()
  
  return NextResponse.json({ 
    message: 'Data received',
    userId: userId,
    data: body
  })
}
```

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from Clerk v5
- Created route matchers for protected routes (`/dashboard`, `/api/protected`)
- Created route matchers for public routes (sign-in, sign-up pages)
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to follow Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async server component
- Added `auth()` to check authentication status
- Added redirect to sign-in if user is not authenticated
- Used `currentUser()` to fetch and display user information
- Added user details display with proper null checking

### 3. **app/api/protected/route.ts**
- Added `auth()` check at the start of the route handler
- Returns 401 Unauthorized if no user is authenticated
- Returns protected data with userId when authenticated
- Added example POST handler showing the same pattern

## How It Works:

1. **Middleware Layer**: The middleware runs on every request matching the config pattern and checks if the route is protected
2. **Server-Side Protection**: Both the dashboard page and API route have additional server-side checks
3. **Automatic Redirects**: Unauthenticated users trying to access protected routes are automatically redirected to sign-in

## Environment Variables Required:

Make sure you have these in your `.env.local`:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

This solution provides defense-in-depth with protection at both the middleware and component/route level!