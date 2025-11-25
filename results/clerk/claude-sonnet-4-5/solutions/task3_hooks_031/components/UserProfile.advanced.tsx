'use client'

import { useUser, useAuth } from '@clerk/nextjs'
import { useRouter } from 'next/navigation'

export default function UserProfile() {
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()
  const { signOut } = useAuth()
  const router = useRouter()

  const handleSignOut = async () => {
    try {
      await signOut()
      router.push('/')
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  if (!userLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isSignedIn) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Not Signed In</h2>
          <p className="text-gray-600 mb-4">Please sign in to continue.</p>
          <button
            onClick={() => router.push('/sign-in')}
            className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
          >
            Sign In
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-start mb-6">
          <h1 className="text-3xl font-bold">User Profile</h1>
          <button
            onClick={handleSignOut}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Sign Out
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Full Name</label>
            <p className="mt-1 text-lg">{user.fullName || 'Not provided'}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Username</label>
            <p className="mt-1 text-lg">{user.username || 'Not set'}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Primary Email</label>
            <p className="mt-1 text-lg">{user.primaryEmailAddress?.emailAddress}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Account Created</label>
            <p className="mt-1 text-lg">
              {user.createdAt ? new Date(user.createdAt).toLocaleString() : 'Unknown'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

## TypeScript Type Definitions