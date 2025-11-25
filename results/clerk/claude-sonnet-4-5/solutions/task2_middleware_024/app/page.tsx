import Link from 'next/link'
import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs'

export default async function Home() {
  const { userId } = auth()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold mb-8">Welcome to Your App</h1>
      
      <div className="flex gap-4 mb-8">
        {userId ? (
          <>
            <UserButton afterSignOutUrl="/" />
            <Link 
              href="/dashboard"
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Go to Dashboard
            </Link>
          </>
        ) : (
          <>
            <SignInButton mode="modal">
              <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Sign Up
              </button>
            </SignUpButton>
          </>
        )}
      </div>

      <p className="text-gray-600">
        {userId ? 'You are signed in!' : 'This is a public page. Sign in to access protected routes.'}
      </p>
    </div>
  )
}