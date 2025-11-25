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