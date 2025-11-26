I'll help you configure Clerk authentication middleware to protect your routes. Here's the complete solution:

```typescript
// filepath: middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define which routes should be protected
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/api/protected(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  // Protect routes that match the protected route matcher
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
  
  // Redirect to sign-in if not authenticated (extra safety check)
  if (!userId) {
    redirect('/sign-in')
  }

  // Get the current user's information
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
import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the auth state
  const { userId } = await auth()

  // Return 401 if not authenticated (extra safety check)
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized' },
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
```

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from `@clerk/nextjs/server`
- Created a route matcher to identify protected routes (`/dashboard` and `/api/protected`)
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async server component
- Added `auth()` to get the current user's authentication state
- Added `currentUser()` to fetch user details
- Added a redirect to sign-in page if user is not authenticated (extra safety)
- Displays user information when authenticated

### 3. **app/api/protected/route.ts**
- Added `auth()` from Clerk to check authentication
- Returns 401 Unauthorized if no userId is present (extra safety)
- Returns protected data including userId when authenticated

## How It Works:

1. **Middleware Protection**: The middleware runs on every request matching the config pattern. When a request hits a protected route, `auth.protect()` automatically redirects unauthenticated users to the sign-in page.

2. **Route Matching**: The `createRouteMatcher` function creates a matcher that checks if the current route should be protected. You can easily add more routes to the array.

3. **Server-Side Auth**: Both the dashboard page and API route use server-side auth helpers to verify authentication state, providing an additional layer of security.

## Environment Variables Required:

Make sure you have these in your `.env.local`:
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

## Testing:

1. Try accessing `/dashboard` - you should be redirected to sign-in if not authenticated
2. Try accessing `/api/protected` - you should get a 401 response if not authenticated
3. After signing in, both routes should work correctly