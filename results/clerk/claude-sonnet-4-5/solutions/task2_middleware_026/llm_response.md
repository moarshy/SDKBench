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
  
  // If no user is signed in, redirect to sign-in page
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
  // Get the auth state
  const { userId } = await auth()

  // If no user is authenticated, return 401
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
- Created a route matcher to identify protected routes (`/dashboard` and `/api/protected`)
- Used `auth.protect()` to enforce authentication on protected routes
- Updated the matcher config to use Clerk's recommended pattern

### 2. **app/dashboard/page.tsx**
- Converted to an async server component
- Added `auth()` to check authentication status
- Added `currentUser()` to fetch user details
- Added redirect logic for unauthenticated users
- Display user information when authenticated

### 3. **app/api/protected/route.ts**
- Added `auth()` to verify authentication
- Return 401 Unauthorized if no userId is present
- Return protected data with userId when authenticated

## How It Works:

1. **Middleware Layer**: The middleware runs on every request matching the config pattern
2. **Route Protection**: Routes matching `/dashboard` or `/api/protected` require authentication
3. **Automatic Redirects**: Clerk automatically redirects unauthenticated users to the sign-in page
4. **Server-Side Auth**: Both the dashboard page and API route verify authentication server-side

## Additional Notes:

- Make sure you have `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` in your `.env.local`
- You can customize the sign-in URL by setting `NEXT_PUBLIC_CLERK_SIGN_IN_URL` and `NEXT_PUBLIC_CLERK_SIGN_UP_URL`
- The middleware will automatically handle redirects to Clerk's hosted sign-in page
- For custom sign-in pages, you can create them at `/sign-in` and `/sign-up` routes