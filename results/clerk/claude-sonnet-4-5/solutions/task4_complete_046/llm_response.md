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
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-medium">
                    {user?.emailAddresses[0]?.emailAddress}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">User ID</p>
                  <p className="font-medium font-mono text-sm">{userId}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Full Name</p>
                  <p className="font-medium">
                    {user?.firstName} {user?.lastName}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Account Created</p>
                  <p className="font-medium">
                    {user?.createdAt
                      ? new Date(user.createdAt).toLocaleDateString()
                      : 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Quick Actions</h3>
              <div className="flex gap-4">
                <button className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition">
                  Edit Profile
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition">
                  Settings
                </button>
              </div>
            </div>
          </div>
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
        fullName: `${user.firstName} ${user.lastName}`,
        imageUrl: user.imageUrl,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt,
        metadata: {
          publicMetadata: user.publicMetadata,
          privateMetadata: user.privateMetadata,
        },
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

// POST endpoint for updating user data
export async function POST(request: Request) {
  try {
    const { userId } = auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in' },
        { status: 401 }
      )
    }

    const body = await request.json()

    // Here you would typically update user data
    // For example, using Clerk's user update API or your database

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

```typescript
// filepath: app/globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Environment Variables Setup

Create a `.env.local` file:

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

## Installation Instructions

```bash
# Install Clerk
npm install @clerk/nextjs

# If using Tailwind CSS (recommended for styling)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

## Summary

This complete integration includes:

1. **Middleware** (`middleware.ts`): Protects routes using `clerkMiddleware()` and `createRouteMatcher()`
2. **Layout** (`app/layout.tsx`): Wraps app with `ClerkProvider` for authentication context
3. **Dashboard** (`app/dashboard/page.tsx`): Protected page with user info and `UserButton`
4. **API Protection** (`app/api/user/route.ts`): Secured API routes with auth checks
5. **Sign-in/Sign-up pages**: Pre-built Clerk components for authentication
6. **User session handling**: Automatic session management by Clerk
7. **Profile management**: User data access and display

All routes under `/dashboard` and `/api/user` are now protected and require authentication!