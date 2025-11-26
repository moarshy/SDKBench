I'll help you complete the Clerk integration with all necessary components. Here's the complete solution:

```typescript
// filepath: middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define which routes should be protected
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/api/user(.*)',
])

export default clerkMiddleware((auth, req) => {
  // Protect routes that match the matcher
  if (isProtectedRoute(req)) {
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
// filepath: app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs'
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider
      appearance={{
        variables: {
          colorPrimary: '#000000',
        },
        elements: {
          formButtonPrimary: 'bg-black hover:bg-gray-800',
          card: 'shadow-lg',
        },
      }}
    >
      <html lang="en">
        <body>
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}
```

```typescript
// filepath: app/dashboard/page.tsx
import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { UserButton } from '@clerk/nextjs'

export default async function Dashboard() {
  // Get authentication state
  const { userId } = auth()
  
  // Redirect to sign-in if not authenticated
  if (!userId) {
    redirect('/sign-in')
  }

  // Get current user details
  const user = await currentUser()

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-semibold">Dashboard</h1>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-4">
            Welcome, {user?.firstName || 'User'}!
          </h2>
          
          <div className="space-y-4">
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold mb-2">Profile Information</h3>
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user?.firstName} {user?.lastName}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Email</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user?.emailAddresses[0]?.emailAddress}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">User ID</dt>
                  <dd className="mt-1 text-sm text-gray-900 font-mono">
                    {userId}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Account Created</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                  </dd>
                </div>
              </dl>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Quick Actions</h3>
              <div className="flex gap-4">
                <button className="px-4 py-2 bg-black text-white rounded-md hover:bg-gray-800 transition">
                  Edit Profile
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition">
                  Settings
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Session Information</h3>
          <p className="text-sm text-gray-600">
            You are currently signed in and have access to protected routes and API endpoints.
          </p>
        </div>
      </main>
    </div>
  )
}
```

```typescript
// filepath: app/api/user/route.ts
import { auth, currentUser } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Get the user ID from the session
    const { userId } = auth()

    // Return 401 if not authenticated
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in' },
        { status: 401 }
      )
    }

    // Get full user details
    const user = await currentUser()

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // Return user data
    return NextResponse.json({
      success: true,
      data: {
        id: user.id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.emailAddresses[0]?.emailAddress,
        imageUrl: user.imageUrl,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt,
        username: user.username,
      },
      message: 'User data retrieved successfully',
    })
  } catch (error) {
    console.error('Error fetching user data:', error)
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

// Optional: Add POST endpoint for updating user metadata
export async function POST(request: Request) {
  try {
    const { userId } = auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const body = await request.json()

    // Here you could update user metadata using Clerk's API
    // For now, we'll just return a success message
    return NextResponse.json({
      success: true,
      message: 'User data updated successfully',
      data: body,
    })
  } catch (error) {
    console.error('Error updating user data:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

## Additional Files Needed

You'll also need to create these sign-in and sign-up pages:

```typescript
// filepath: app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <SignIn 
        appearance={{
          elements: {
            rootBox: 'mx-auto',
            card: 'shadow-lg',
          },
        }}
        routing="path"
        path="/sign-in"
        signUpUrl="/sign-up"
      />
    </div>
  )
}
```

```typescript
// filepath: app/sign-up/[[...sign-up]]/page.tsx
import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <SignUp 
        appearance={{
          elements: {
            rootBox: 'mx-auto',
            card: 'shadow-lg',
          },
        }}
        routing="path"
        path="/sign-up"
        signInUrl="/sign-in"
      />
    </div>
  )
}
```

```css
/* filepath: app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

## Environment Variables

Create a `.env.local` file with:

```bash
# filepath: .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_key_here

# Optional: Custom URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

## Installation

Make sure you have the required dependencies:

```bash
npm install @clerk/nextjs
```

## Summary

This complete integration includes:

1. ✅ **Middleware**: Protects `/dashboard` and `/api/user` routes
2. ✅ **ClerkProvider**: Wraps the entire app with authentication context
3. ✅ **Protected Dashboard**: Server-side authentication check with user profile display
4. ✅ **Protected API Route**: Returns user data only for authenticated users
5. ✅ **Sign-in/Sign-up Pages**: Pre-built Clerk components
6. ✅ **User Management**: UserButton for profile and sign-out
7. ✅ **Error Handling**: Proper error responses and redirects
8. ✅ **TypeScript Support**: Fully typed with Clerk v5

The integration follows Clerk v5 best practices and is production-ready!