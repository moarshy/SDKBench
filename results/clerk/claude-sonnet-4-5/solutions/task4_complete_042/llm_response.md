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
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
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
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-700">User ID:</span>
                  <span className="text-gray-600">{userId}</span>
                </div>
                {user?.emailAddresses?.[0]?.emailAddress && (
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-700">Email:</span>
                    <span className="text-gray-600">
                      {user.emailAddresses[0].emailAddress}
                    </span>
                  </div>
                )}
                {user?.firstName && (
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-700">Name:</span>
                    <span className="text-gray-600">
                      {user.firstName} {user.lastName}
                    </span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-700">
                    Created At:
                  </span>
                  <span className="text-gray-600">
                    {new Date(user?.createdAt || '').toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                Protected Content
              </h3>
              <p className="text-blue-800">
                This page is protected by Clerk middleware. Only authenticated
                users can access this content.
              </p>
            </div>

            <div className="mt-6">
              <a
                href="/api/user"
                className="inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Test Protected API Route
              </a>
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
    // Get the authentication state
    const { userId } = auth()

    // Check if user is authenticated
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in' },
        { status: 401 }
      )
    }

    // Get the current user's details
    const user = await currentUser()

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // Return user data
    return NextResponse.json({
      message: 'User data retrieved successfully',
      user: {
        id: user.id,
        email: user.emailAddresses[0]?.emailAddress,
        firstName: user.firstName,
        lastName: user.lastName,
        imageUrl: user.imageUrl,
        createdAt: user.createdAt,
        lastSignInAt: user.lastSignInAt,
      },
    })
  } catch (error) {
    console.error('Error fetching user data:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Optional: Add POST endpoint for updating user data
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

    // Here you would typically update user metadata or perform other operations
    // For example: await clerkClient.users.updateUserMetadata(userId, { ... })

    return NextResponse.json({
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
            rootBox: "mx-auto",
            card: "shadow-lg"
          }
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
            rootBox: "mx-auto",
            card: "shadow-lg"
          }
        }}
        routing="path"
        path="/sign-up"
        signInUrl="/sign-in"
      />
    </div>
  )
}
```

```typescript
// filepath: app/page.tsx
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'

export default function Home() {
  const { userId } = auth()

  // If user is signed in, redirect to dashboard
  if (userId) {
    redirect('/dashboard')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
        <h1 className="text-4xl font-bold text-center text-gray-900 mb-4">
          Welcome
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Complete Clerk Integration with Next.js
        </p>
        
        <div className="space-y-4">
          <Link
            href="/sign-in"
            className="block w-full py-3 px-4 bg-blue-600 text-white text-center rounded-md hover:bg-blue-700 transition-colors font-medium"
          >
            Sign In
          </Link>
          
          <Link
            href="/sign-up"
            className="block w-full py-3 px-4 bg-gray-200 text-gray-800 text-center rounded-md hover:bg-gray-300 transition-colors font-medium"
          >
            Sign Up
          </Link>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <h2 className="text-sm font-semibold text-gray-700 mb-2">
            Features Included:
          </h2>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>✓ Complete authentication flow</li>
            <li>✓ Protected routes with middleware</li>
            <li>✓ Protected API endpoints</li>
            <li>✓ User session management</li>
            <li>✓ User profile access</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
```

```css
/* filepath: app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-start-rgb: 214, 219, 220;
  --background-end-rgb: 255, 255, 255;
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
}
```

## Environment Variables

Create a `.env.local` file with your Clerk keys:

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

1. **Initialization**: ClerkProvider wraps the entire app in `layout.tsx`
2. **Configuration**: Environment variables and appearance customization
3. **Middleware**: Route protection in `middleware.ts` using `clerkMiddleware()`
4. **API Protection**: Protected API route in `app/api/user/route.ts`
5. **Sign-in/Sign-up**: Dedicated pages for authentication
6. **Dashboard**: Protected page showing user information
7. **Home Page**: Landing page with navigation

All routes are properly protected, and the integration follows Clerk v5 best practices!