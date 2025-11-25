import Link from 'next/link'
import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs'

export default async function Home() {
  const { userId } = await auth()

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-8">Welcome to Your App</h1>
        
        {userId ? (
          <div className="space-y-4">
            <p className="text-lg mb-4">You are signed in!</p>
            <div className="flex gap-4 justify-center items-center">
              <UserButton afterSignOutUrl="/" />
              <Link
                href="/dashboard"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >
                Go to Dashboard
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-lg mb-4">Please sign in to continue</p>
            <div className="flex gap-4 justify-center">
              <SignInButton mode="modal">
                <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                  Sign Up
                </button>
              </SignUpButton>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}