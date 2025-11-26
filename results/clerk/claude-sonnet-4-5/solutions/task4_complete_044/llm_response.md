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
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <SignOutButton>
              <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                Sign Out
              </button>
            </SignOutButton>
          </div>

          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Welcome back!
            </h2>
            
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-sm font-medium text-gray-500">User ID</p>
                <p className="mt-1 text-sm text-gray-900">{userId}</p>
              </div>

              {user?.emailAddresses && user.emailAddresses.length > 0 && (
                <div className="bg-gray-50 p-4 rounded-md">
                  <p className="text-sm font-medium text-gray-500">Email</p>
                  <p className="mt-1 text-sm text-gray-900">
                    {user.emailAddresses[0].emailAddress}
                  </p>
                </div>
              )}

              {user?.firstName && (
                <div className="bg-gray-50 p-4 rounded-md">
                  <p className="text-sm font-medium text-gray-500">Name</p>
                  <p className="mt-1 text-sm text-gray-900">
                    {user.firstName} {user.lastName || ''}
                  </p>
                </div>
              )}

              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-sm font-medium text-gray-500">
                  Account Created
                </p>
                <p className="mt-1 text-sm text-gray-900">
                  {user?.createdAt 
                    ? new Date(user.createdAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })
                    : 'N/A'}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-3">
              Quick Actions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <a
                href="/user-profile"
                className="block p-4 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
              >
                <p className="font-medium text-blue-900">Edit Profile</p>
                <p className="text-sm text-blue-700 mt-1">
                  Update your account information
                </p>
              </a>
              <a
                href="/api/user"
                className="block p-4 bg-green-50 hover:bg-green-100 rounded-md transition-colors"
              >
                <p className="font-medium text-green-900">API Test</p>
                <p className="text-sm text-green-700 mt-1">
                  Test protected API endpoint
                </p>
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

    // Return 401 if not authenticated
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
      success: true,
      data: {
        userId: user.id,
        email: user.emailAddresses[0]?.emailAddress || null,
        firstName: user.firstName,
        lastName: user.lastName,
        fullName: `${user.firstName || ''} ${user.lastName || ''}`.trim(),
        imageUrl: user.imageUrl,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt,
        lastSignInAt: user.lastSignInAt,
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

    // Here you could update user metadata or perform other operations
    // For example, using Clerk's clerkClient:
    // await clerkClient.users.updateUserMetadata(userId, {
    //   publicMetadata: body.publicMetadata,
    //   privateMetadata: body.privateMetadata,
    // })

    return NextResponse.json({
      success: true,
      message: 'User data updated successfully',
      userId,
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

## Additional Required Files

You'll also need to create these additional files for a complete integration:

```typescript
// filepath: app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <SignIn 
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-lg"
            }
          }}
        />
      </div>
    </div>
  )
}
```

```typescript
// filepath: app/sign-up/[[...sign-up]]/page.tsx
import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <SignUp 
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-lg"
            }
          }}
        />
      </div>
    </div>
  )
}
```

```typescript
// filepath: app/user-profile/[[...user-profile]]/page.tsx
import { UserProfile } from '@clerk/nextjs'

export default function UserProfilePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Profile Settings
        </h1>
        <UserProfile 
          appearance={{
            elements: {
              rootBox: "w-full",
              card: "shadow-lg"
            }
          }}
        />
      </div>
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-5xl font-extrabold text-gray-900 mb-4">
            Welcome to Your App
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Secure authentication powered by Clerk
          </p>
          
          <div className="flex justify-center gap-4">
            <Link
              href="/sign-in"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg text-lg font-semibold transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/sign-up"
              className="bg-white hover:bg-gray-50 text-blue-600 px-8 py-3 rounded-lg text-lg font-semibold border-2 border-blue-600 transition-colors"
            >
              Sign Up
            </Link>
          </div>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              🔒 Secure Authentication
            </h3>
            <p className="text-gray-600">
              Enterprise-grade security with Clerk's authentication system
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              ⚡ Fast Integration
            </h3>
            <p className="text-gray-600">
              Get up and running in minutes with our pre-built components
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              👤 User Management
            </h3>
            <p className="text-gray-600">
              Complete user profile and session management out of the box
            </p>
          </div>
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

```env
# filepath: .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_publishable_key_here
CLERK_SECRET_KEY=your_secret_key_here

# Optional: Customize sign-in/up URLs
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
   - Copy `.env.local` and add your Clerk keys from the [Clerk Dashboard](https://dashboard.clerk.com)

3. **The integration includes:**
   - ✅ ClerkProvider wrapping the app
   - ✅ Middleware protecting routes
   - ✅ Protected dashboard page
   