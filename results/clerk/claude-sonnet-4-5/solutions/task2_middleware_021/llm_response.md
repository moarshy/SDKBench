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
  
  // Redirect to sign-in if not authenticated (extra safety check)
  if (!userId) {
    redirect('/sign-in')
  }

  // Get the current user's information
  const user = await currentUser()

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <p className="mb-4">
        Welcome, {user?.firstName || user?.emailAddresses[0]?.emailAddress || 'User'}!
      </p>
      <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
        <p className="font-bold">✓ This route is now protected</p>
        <p className="text-sm mt-2">
          User ID: {userId}
        </p>
        {user?.emailAddresses[0]?.emailAddress && (
          <p className="text-sm">
            Email: {user.emailAddresses[0].emailAddress}
          </p>
        )}
      </div>
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

  // Return 401 if not authenticated
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }

  // Get user information
  const user = await currentUser()

  // Return protected data
  return NextResponse.json({
    message: 'This route is now protected',
    userId: userId,
    userEmail: user?.emailAddresses[0]?.emailAddress,
    timestamp: new Date().toISOString(),
  })
}

// Example POST endpoint
export async function POST(request: Request) {
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }

  try {
    const body = await request.json()
    
    // Process the request with authenticated user context
    return NextResponse.json({
      message: 'Data processed successfully',
      userId: userId,
      data: body,
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request body' },
      { status: 400 }
    )
  }
}
```

## Key Features Implemented:

### 1. **Middleware (middleware.ts)**
- Uses `clerkMiddleware()` from Clerk v5
- Defines protected routes using `createRouteMatcher()`
- Protects `/dashboard` and `/api/protected` routes
- Uses `auth.protect()` to enforce authentication
- Optimized matcher configuration to skip static files

### 2. **Dashboard Page (app/dashboard/page.tsx)**
- Server component with authentication check
- Uses `auth()` to get user ID
- Uses `currentUser()` to get full user details
- Displays user information
- Includes redirect as extra safety measure

### 3. **Protected API Route (app/api/protected/route.ts)**
- Checks authentication using `auth()`
- Returns 401 for unauthorized requests
- Includes both GET and POST examples
- Returns user context in responses

## Environment Variables Required:

Make sure you have these in your `.env.local`:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

## Testing:

1. **Unauthenticated users**: Will be redirected to sign-in when accessing `/dashboard`
2. **API routes**: Will return 401 when accessed without authentication
3. **Authenticated users**: Can access all protected routes and see their user information

The middleware now properly protects your routes while allowing public access to sign-in/sign-up pages!