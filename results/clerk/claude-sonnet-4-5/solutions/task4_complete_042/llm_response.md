I'll help you complete the Clerk integration with all necessary components. Here's the complete solution:

```typescript
// filepath: middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define protected routes that require authentication
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/api/user(.*)',
])

export default clerkMiddleware((auth, req) => {
  // Protect routes that match the pattern
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
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <SignOutButton>
              <button className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition">
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

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-semibold text-gray-700 mb-2">User ID</h3>
                <p className="text-sm text-gray-600 font-mono break-all">
                  {userId}
                </p>
              </div>

              {user?.emailAddresses?.[0]?.emailAddress && (
                <div className="bg-gray-50 p-4 rounded">
                  <h3 className="font-semibold text-gray-700 mb-2">Email</h3>
                  <p className="text-sm text-gray-600">
                    {user.emailAddresses[0].emailAddress}
                  </p>
                </div>
              )}

              {user?.firstName && (
                <div className="bg-gray-50 p-4 rounded">
                  <h3 className="font-semibold text-gray-700 mb-2">
                    First Name
                  </h3>
                  <p className="text-sm text-gray-600">{user.firstName}</p>
                </div>
              )}

              {user?.lastName && (
                <div className="bg-gray-50 p-4 rounded">
                  <h3 className="font-semibold text-gray-700 mb-2">
                    Last Name
                  </h3>
                  <p className="text-sm text-gray-600">{user.lastName}</p>
                </div>
              )}
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded">
              <h3 className="font-semibold text-blue-900 mb-2">
                Protected Content
              </h3>
              <p className="text-sm text-blue-800">
                This page is protected by Clerk middleware. Only authenticated
                users can access this content.
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

    // Return 401 if not authenticated
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in' },
        { status: 401 }
      )
    }

    // Get current user details
    const user = await currentUser()

    // Return user data
    return NextResponse.json({
      message: 'User data retrieved successfully',
      user: {
        id: userId,
        email: user?.emailAddresses?.[0]?.emailAddress,
        firstName: user?.firstName,
        lastName: user?.lastName,
        username: user?.username,
        imageUrl: user?.imageUrl,
        createdAt: user?.createdAt,
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
```

## Additional Required Files

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

Install the required package:

```bash
npm install @clerk/nextjs
```

## Summary

This complete integration includes:

1. **Middleware** (`middleware.ts`): Protects `/dashboard` and `/api/user` routes
2. **Layout** (`app/layout.tsx`): Wraps app with ClerkProvider
3. **Dashboard** (`app/dashboard/page.tsx`): Protected page showing user info with sign-out
4. **API Route** (`app/api/user/route.ts`): Protected endpoint returning user data
5. **Sign-in/Sign-up pages**: Pre-built Clerk components for authentication
6. **Error handling**: Proper 401 responses and redirects
7. **User session management**: Automatic session handling by Clerk

The solution follows Clerk v5 best practices and is production-ready!