import Link from 'next/link'
import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs'

export default async function Home() {
  const { userId } = await auth()

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold mb-8">Welcome to My App</h1>
      
      <div className="flex gap-4 mb-8">
        {userId ? (
          <>
            <UserButton afterSignOutUrl="/" />
            <Link 
              href="/dashboard"
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Go to Dashboard
            </Link>
          </>
        ) : (
          <>
            <SignInButton mode="modal">
              <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Sign Up
              </button>
            </SignUpButton>
          </>
        )}
      </div>

      <p className="text-gray-600">
        {userId ? 'You are signed in!' : 'Please sign in to access protected routes'}
      </p>
    </div>
  )
}

## Key Features Implemented:

1. **Middleware Protection**: Routes are automatically protected unless explicitly marked as public
2. **Route Matchers**: Uses `createRouteMatcher` for clean route definitions
3. **Protected Dashboard**: Server-side authentication check with user data
4. **Protected API**: Authentication validation in API routes
5. **Public Routes**: Home page and auth pages are accessible without login
6. **Proper Redirects**: Automatic redirects to sign-in for protected routes
7. **User Management**: Integration of Clerk UI components

## Testing the Implementation:

1. **Test Protected Route**: Navigate to `/dashboard` - should redirect to sign-in
2. **Test Protected API**: Call `/api/protected` - should return 401 without auth
3. **Test Public Route**: Visit `/` - should be accessible
4. **Test After Sign-In**: Sign in and access `/dashboard` - should work
5. **Test API After Auth**: Call `/api/protected` when signed in - should return data

This implementation follows Clerk v5 best practices and provides a secure, production-ready authentication setup!