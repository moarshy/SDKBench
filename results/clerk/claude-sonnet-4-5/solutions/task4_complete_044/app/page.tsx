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