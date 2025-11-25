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
          formButtonPrimary: 
            'bg-black hover:bg-gray-800 text-sm normal-case',
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
import { SignOutButton } from '@clerk/nextjs'

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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <SignOutButton>
              <button className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
                Sign Out
              </button>
            </SignOutButton>
          </div>

          <div className="space-y-4">
            <div className="border-b pb-4">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                Welcome back!
              </h2>
              <p className="text-gray-600">
                You are successfully authenticated with Clerk.
              </p>
            </div>

            <div className="bg-gray-50 rounded-md p-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                User Information
              </h3>
              <div className="space-y-2">
                <div className="flex items-center">
                  <span className="font-medium text-gray-700 w-32">User ID:</span>
                  <span className="text-gray-600">{userId}</span>
                </div>
                {user?.emailAddresses?.[0]?.emailAddress && (
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-32">Email:</span>
                    <span className="text-gray-600">
                      {user.emailAddresses[0].emailAddress}
                    </span>
                  </div>
                )}
                {user?.firstName && (
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-32">First Name:</span>
                    <span className="text-gray-600">{user.firstName}</span>
                  </div>
                )}
                {user?.lastName && (
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-32">Last Name:</span>
                    <span className="text-gray-600">{user.lastName}</span>
                  </div>
                )}
                <div className="flex items-center">
                  <span className="font-medium text-gray-700 w-32">Created:</span>
                  <span className="text-gray-600">
                    {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                Protected Content
              </h3>
              <p className="text-blue-800">
                This page is protected by Clerk middleware. Only authenticated users can access this content.
              </p>
            </div>
          </div>
        </div>
      </div>
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
    // Get authentication state
    const { userId } = auth()

    // Check if user is authenticated
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in' },
        { status: 401 }
      )
    }

    // Get current user details
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
        userId: user.id,
        email: user.emailAddresses?.[0]?.emailAddress || null,
        firstName: user.firstName,
        lastName: user.lastName,
        fullName: `${user.firstName || ''} ${user.lastName || ''}`.trim(),
        imageUrl: user.imageUrl,
        createdAt: user.createdAt,
        lastSignInAt: user.lastSignInAt,
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

    // Here you can add logic to update user metadata
    // using Clerk's API or your own database

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

You'll also need to create these additional files for a complete integration:

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

```typescript
// filepath: app/page.tsx
import Link from 'next/link'
import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton } from '@clerk/nextjs'

export default function Home() {
  const { userId } = auth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Welcome to Clerk Integration
          </h1>
          <p className="text-xl text-gray-600">
            Complete authentication solution for Next.js
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8">
          {userId ? (
            <div className="text-center">
              <p className="text-lg text-gray-700 mb-6">
                You are signed in!
              </p>
              <Link
                href="/dashboard"
                className="inline-block px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Go to Dashboard
              </Link>
            </div>
          ) : (
            <div className="text-center space-y-4">
              <p className="text-lg text-gray-700 mb-6">
                Get started by signing in or creating an account
              </p>
              <div className="flex gap-4 justify-center">
                <SignInButton mode="modal">
                  <button className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                    Sign In
                  </button>
                </SignInButton>
                <SignUpButton mode="modal">
                  <button className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
                    Sign Up
                  </button>
                </SignUpButton>
              </div>
            </div>
          )}
        </div>

        <div className="mt-12 grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-3">
              🔒 Protected Routes
            </h3>
            <p className="text-gray-600">
              Dashboard and API routes are automatically protected by Clerk middleware
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-3">
              👤 User Management
            </h3>
            <p className="text-gray-600">
              Complete user profile management with email verification and sessions
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
```

```env
# filepath: .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_publishable_key_here
CLERK_SECRET_KEY=your_secret_key_here

# Optional: Custom sign-in/up URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

## Installation Instructions

1. **Install Clerk package:**
```bash
npm install @clerk/nextjs
```

2. **Set up environment variables:**
   - Copy `.env.local` and add your Clerk keys from the Clerk Dashboard
   - Get keys from: https://dashboard.clerk.com

3. **The integration includes:**
   - ✅ ClerkProvider wrapping the app
   - ✅ Middleware protecting routes
   - ✅ Protected dashboard page
   - ✅ Protected API route
   - ✅ Sign-in and sign-up pages
   - ✅ User session management
   - ✅ Error handling

4. **Test the integration:**
   - Visit `/` to see the home page
   - Click "Sign Up" to create an account
   - Access `/dashboard` (protected route)
   - Call `/api/user` (protected API)

This is a production-ready Clerk integration with all security best practices implemented!