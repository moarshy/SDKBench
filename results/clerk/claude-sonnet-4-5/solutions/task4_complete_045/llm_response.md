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
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <a
                href="/user-profile"
                className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
              >
                Edit Profile
              </a>
              <button
                onClick={() => {
                  fetch('/api/user')
                    .then(res => res.json())
                    .then(data => alert(JSON.stringify(data, null, 2)))
                    .catch(err => alert('Error: ' + err.message))
                }}
                className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
              >
                Test API Route
              </button>
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
    // Get the userId from auth
    const { userId } = auth()

    // Check if user is authenticated
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in' },
        { status: 401 }
      )
    }

    // Get the full user object
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
        username: user.username,
        imageUrl: user.imageUrl,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt,
      },
    })
  } catch (error) {
    console.error('Error in /api/user:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
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
      message: 'User updated successfully',
      userId,
    })
  } catch (error) {
    console.error('Error updating user:', error)
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
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
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
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
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
// filepath: app/user-profile/[[...user-profile]]/page.tsx
import { UserProfile } from '@clerk/nextjs'

export default function UserProfilePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <UserProfile 
        appearance={{
          elements: {
            rootBox: "mx-auto",
            card: "shadow-lg"
          }
        }}
        routing="path"
        path="/user-profile"
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
            Welcome to Your App
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Get started by signing in or creating a new account
          </p>
          <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
            <div className="rounded-md shadow">
              <Link
                href="/sign-in"
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10"
              >
                Sign In
              </Link>
            </div>
            <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
              <Link
                href="/sign-up"
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
              >
                Sign Up
              </Link>
            </div>
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

```env
# filepath: .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_key_here

# Optional: Custom URLs
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
   - ✅ Protected API route
   - ✅ Sign-in and sign-up pages
   - ✅ User profile management
   - ✅ Session handling
   - ✅ Error handling

4. **Test the integration:**
   - Visit `/` - Home page with sign-in/sign-up links
   - Visit `/sign-in` - Sign in page
   - Visit `/sign-up` - Sign up page
   - Visit `/dashboard` - Protected dashboard (redirects if not authenticated)
   - Visit `/api/user` - Protected API route
   - Visit `/user-profile` - User profile management

The integration is now complete with all authentication flows, route protection, and user management features!