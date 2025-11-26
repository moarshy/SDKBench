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