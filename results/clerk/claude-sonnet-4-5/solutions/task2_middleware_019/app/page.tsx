import { auth } from '@clerk/nextjs/server'
import Link from 'next/link'

export default function Home() {
  const { userId } = auth()

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">Welcome to Your App</h1>
      
      {userId ? (
        <div className="space-y-4">
          <p className="text-lg">You are signed in!</p>
          <Link
            href="/dashboard"
            className="block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Go to Dashboard
          </Link>
        </div>
      ) : (
        <div className="space-x-4">
          <Link
            href="/sign-in"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Sign In
          </Link>
          <Link
            href="/sign-up"
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Sign Up
          </Link>
        </div>
      )}
    </div>
  )
}

## Key Features Implemented:

1. **Middleware Protection**: Uses `clerkMiddleware()` with `auth().protect()` to secure routes
2. **Route Matchers**: Defines public and protected routes clearly
3. **API Protection**: Both middleware and route-level authentication checks
4. **User Data Access**: Shows how to get user information in protected routes
5. **Proper Redirects**: Configured sign-in/sign-up flows
6. **Error Handling**: Returns appropriate HTTP status codes for unauthorized access

## Testing the Implementation:

1. Try accessing `/dashboard` without signing in → Should redirect to sign-in
2. Try accessing `/api/protected` without auth → Should return 401
3. Sign in and access `/dashboard` → Should show user info
4. Access `/api/public` → Should work without authentication

This setup provides a secure, production-ready authentication system using Clerk v5!