I'll help you configure Clerk authentication middleware to protect your routes. Here's the complete solution:

```typescript
// filepath: middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)',
])

export default clerkMiddleware((auth, request) => {
  // Protect all routes except public ones
  if (!isPublicRoute(request)) {
    auth().protect()
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
  const { userId } = auth()
  
  // Redirect to sign-in if not authenticated
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
import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the authentication state
  const { userId } = auth()

  // Return 401 if not authenticated
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized - Please sign in' },
      { status: 401 }
    )
  }

  // Return protected data
  return NextResponse.json({
    message: 'This is protected data',
    userId: userId,
    timestamp: new Date().toISOString(),
  })
}
```

## Key Changes Made:

### 1. **middleware.ts**
- Imported `clerkMiddleware` and `createRouteMatcher` from `@clerk/nextjs/server`
- Defined public routes using `createRouteMatcher` (home, sign-in, sign-up pages)
- Used `auth().protect()` to protect all non-public routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Imported `auth` and `currentUser` from `@clerk/nextjs/server`
- Added server-side authentication check using `auth()`
- Redirects to sign-in if user is not authenticated
- Displays user information when authenticated
- Made it an async server component to use Clerk's server helpers

### 3. **app/api/protected/route.ts**
- Imported `auth` from `@clerk/nextjs/server`
- Added authentication check at the API route level
- Returns 401 Unauthorized if user is not authenticated
- Returns protected data with userId when authenticated

## How It Works:

1. **Middleware Layer**: The middleware runs on every request and protects all routes except those defined in `isPublicRoute`
2. **Server Components**: The dashboard uses `auth()` to verify authentication server-side
3. **API Routes**: The protected API route checks authentication and returns appropriate responses

## Environment Variables Required:

Make sure you have these in your `.env.local`:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

## Testing:

1. Unauthenticated users trying to access `/dashboard` will be redirected to sign-in
2. Unauthenticated API calls to `/api/protected` will receive a 401 error
3. Authenticated users can access both the dashboard and API route successfully