import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs'
import Link from 'next/link'

export default async function Home() {
  const { userId } = auth()

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">My App</h1>
            </div>
            <div className="flex items-center gap-4">
              {userId ? (
                <>
                  <Link 
                    href="/dashboard"
                    className="text-gray-700 hover:text-gray-900 font-medium"
                  >
                    Dashboard
                  </Link>
                  <UserButton afterSignOutUrl="/" />
                </>
              ) : (
                <>
                  <SignInButton mode="modal">
                    <button className="text-gray-700 hover:text-gray-900 font-medium">
                      Sign In
                    </button>
                  </SignInButton>
                  <SignUpButton mode="modal">
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium">
                      Sign Up
                    </button>
                  </SignUpButton>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to Your Protected App
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            {userId 
              ? 'You are signed in! Visit your dashboard to see protected content.'
              : 'Sign in to access protected routes and features.'
            }
          </p>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto mt-12">
            <div className="bg-white p-6 rounded-lg shadow-md border">
              <h3 className="text-lg font-semibold mb-2">🔒 Protected Routes</h3>
              <p className="text-gray-600 mb-4">
                Dashboard and API routes are protected by Clerk middleware
              </p>
              <Link 
                href="/dashboard"
                className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Go to Dashboard
              </Link>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <h3 className="text-lg font-semibold mb-2">🌐 Public Routes</h3>
              <p className="text-gray-600 mb-4">
                Home page and public API routes are accessible to everyone
              </p>
              <a 
                href="/api/public"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
              >
                Test Public API
              </a>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

### 9. Environment Variables