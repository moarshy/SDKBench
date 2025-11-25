import Link from 'next/link'
import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs'

export default async function Home() {
  const { userId } = await auth()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">
            Welcome to Clerk + Next.js
          </h1>
          <p className="text-gray-600 mb-8">
            This is a public page. Authentication is configured and working!
          </p>
        </div>

        <div className="flex justify-center gap-4">
          {userId ? (
            <>
              <UserButton afterSignOutUrl="/" />
              <Link
                href="/dashboard"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Go to Dashboard
              </Link>
            </>
          ) : (
            <>
              <SignInButton mode="modal">
                <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
                  Sign Up
                </button>
              </SignUpButton>
            </>
          )}
        </div>

        <div className="mt-12 p-6 bg-gray-100 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Route Protection Status:</h2>
          <ul className="space-y-2">
            <li className="flex items-center gap-2">
              <span className="text-green-600">✓</span>
              <span><code>/</code> - Public (this page)</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-red-600">🔒</span>
              <span><code>/dashboard</code> - Protected</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-red-600">🔒</span>
              <span><code>/api/protected</code> - Protected API</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-green-600">✓</span>
              <span><code>/api/public</code> - Public API</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}