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