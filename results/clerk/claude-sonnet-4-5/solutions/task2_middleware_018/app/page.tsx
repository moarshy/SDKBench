import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton } from '@clerk/nextjs'
import Link from 'next/link'

export default async function Home() {
  const { userId } = await auth()

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">Welcome</h1>
          <p className="text-gray-600 mb-8">
            {userId 
              ? 'You are signed in!' 
              : 'Please sign in to access protected routes'}
          </p>
        </div>

        {userId ? (
          <div className="space-y-4">
            <Link
              href="/dashboard"
              className="block w-full text-center bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition"
            >
              Go to Dashboard
            </Link>
            <Link
              href="/api/protected"
              className="block w-full text-center bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 transition"
            >
              Test Protected API
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            <SignInButton mode="modal">
              <button className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 transition">
                Sign Up
              </button>
            </SignUpButton>
          </div>
        )}
      </div>
    </div>
  )
}