import Link from 'next/link'
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default function Home() {
  const { userId } = auth()

  // If user is already signed in, redirect to dashboard
  if (userId) {
    redirect('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Welcome to Clerk Integration
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Complete authentication solution with Next.js
          </p>
          
          <div className="flex justify-center gap-4">
            <Link
              href="/sign-in"
              className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition font-semibold"
            >
              Sign In
            </Link>
            <Link
              href="/sign-up"
              className="px-8 py-3 bg-white text-black border-2 border-black rounded-lg hover:bg-gray-50 transition font-semibold"
            >
              Sign Up
            </Link>
          </div>

          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-2">🔒 Secure</h3>
              <p className="text-gray-600">
                Enterprise-grade security with Clerk authentication
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-2">⚡ Fast</h3>
              <p className="text-gray-600">
                Lightning-fast authentication with optimized middleware
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-2">🎨 Customizable</h3>
              <p className="text-gray-600">
                Fully customizable UI components and flows
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}