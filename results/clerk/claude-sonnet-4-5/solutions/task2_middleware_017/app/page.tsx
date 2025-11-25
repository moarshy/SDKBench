import Link from 'next/link'
import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs'

export default async function Home() {
  const { userId } = auth()

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">Welcome to My App</h1>
      
      <div className="flex gap-4 mb-8">
        {userId ? (
          <>
            <UserButton afterSignOutUrl="/" />
            <Link 
              href="/dashboard"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Go to Dashboard
            </Link>
          </>
        ) : (
          <>
            <SignInButton mode="modal">
              <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
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
2. **Public Routes**: Home, sign-in, sign-up, and public API routes are accessible without auth
3. **Protected Routes**: Dashboard and protected API routes require authentication
4. **Server-Side Auth**: Uses `auth()` helper for server components and API routes
5. **User Information**: Access to current user data in protected routes
6. **Proper Error Handling**: 401 responses for unauthorized API requests
7. **Flexible Configuration**: Easy to add more public or protected routes

## Testing the Implementation:

1. **Without Authentication**:
   - Visit `/` - Should work (public)
   - Visit `/dashboard` - Should redirect to sign-in
   - Call `/api/protected` - Should return 401
   - Call `/api/public` - Should work

2. **With Authentication**:
   - Sign in via `/sign-in`
   - Visit `/dashboard` - Should display user info
   - Call `/api/protected` - Should return protected data

This setup provides a robust, production-ready authentication system using Clerk v5!