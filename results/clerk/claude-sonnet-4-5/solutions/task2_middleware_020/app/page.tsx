import Link from 'next/link'
import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs'

export default async function Home() {
  const { userId } = auth()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold mb-8">Welcome to Your App</h1>
      
      <div className="mb-8">
        {userId ? (
          <div className="flex items-center gap-4">
            <UserButton afterSignOutUrl="/" />
            <Link 
              href="/dashboard"
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
            >
              Go to Dashboard
            </Link>
          </div>
        ) : (
          <div className="flex gap-4">
            <SignInButton mode="modal">
              <button className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600">
                Sign Up
              </button>
            </SignUpButton>
          </div>
        )}
      </div>

      <div className="text-center">
        <p className="text-gray-600 mb-4">
          {userId ? 'You are signed in!' : 'Please sign in to access protected routes'}
        </p>
        <Link href="/dashboard" className="text-blue-500 hover:underline">
          Try accessing the protected dashboard →
        </Link>
      </div>
    </div>
  )
}