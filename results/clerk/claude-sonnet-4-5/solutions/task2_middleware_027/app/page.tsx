import { auth } from '@clerk/nextjs/server'
import Link from 'next/link'

export default async function Home() {
  const { userId } = auth()

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">Welcome to My App</h1>
      
      {userId ? (
        <div className="space-y-4">
          <p className="text-lg">You are signed in!</p>
          <Link 
            href="/dashboard"
            className="block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Go to Dashboard
          </Link>
        </div>
      ) : (
        <div className="space-x-4">
          <Link 
            href="/sign-in"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Sign In
          </Link>
          <Link 
            href="/sign-up"
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Sign Up
          </Link>
        </div>
      )}
    </div>
  )
}