import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton } from '@clerk/nextjs'
import Link from 'next/link'

export default async function Home() {
  const { userId } = await auth()

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">Welcome to Your App</h1>
      
      {userId ? (
        <div className="space-y-4 text-center">
          <p className="text-xl">You are signed in!</p>
          <Link
            href="/dashboard"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
          >
            Go to Dashboard
          </Link>
        </div>
      ) : (
        <div className="space-x-4">
          <SignInButton mode="modal">
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition">
              Sign In
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition">
              Sign Up
            </button>
          </SignUpButton>
        </div>
      )}
    </div>
  )
}