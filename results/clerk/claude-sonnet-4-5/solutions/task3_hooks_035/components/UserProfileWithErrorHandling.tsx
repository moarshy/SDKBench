'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { SignInButton, SignOutButton } from '@clerk/nextjs'
import { useEffect, useState } from 'react'

export default function UserProfileWithErrorHandling() {
  const { isLoaded: authLoaded, userId } = useAuth()
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Check for potential errors after loading
    if (authLoaded && userLoaded) {
      if (isSignedIn && !user) {
        setError('Failed to load user data. Please try refreshing the page.')
      }
    }
  }, [authLoaded, userLoaded, isSignedIn, user])

  // Loading state
  if (!authLoaded || !userLoaded) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="p-8 max-w-md mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-red-800 font-semibold mb-2">Error</h2>
          <p className="text-red-700">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Refresh Page
          </button>
        </div>
      </div>
    )
  }

  // Not signed in
  if (!isSignedIn) {
    return (
      <div className="p-8 max-w-md mx-auto text-center">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600 mb-6">
          Please sign in to view your profile
        </p>
        <SignInButton mode="modal">
          <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            Sign In
          </button>
        </SignInButton>
      </div>
    )
  }

  // Signed in - display user data
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">User Profile</h1>
      <div className="bg-white shadow rounded-lg p-6 space-y-4">
        {user.imageUrl && (
          <img
            src={user.imageUrl}
            alt="Profile"
            className="w-24 h-24 rounded-full"
          />
        )}
        <div>
          <p className="text-sm text-gray-600">User ID</p>
          <p className="font-mono text-sm">{userId}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Full Name</p>
          <p>{user.fullName || 'Not set'}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Email</p>
          <p>{user.primaryEmailAddress?.emailAddress || 'Not set'}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Username</p>
          <p>{user.username || 'Not set'}</p>
        </div>
        <SignOutButton>
          <button className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 mt-4">
            Sign Out
          </button>
        </SignOutButton>
      </div>
    </div>
  )
}

## TypeScript Types Reference