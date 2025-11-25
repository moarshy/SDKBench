'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { useEffect, useState } from 'react'

export default function UserProfileWithErrorBoundary() {
  const { isLoaded: authLoaded, userId } = useAuth()
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Check for potential errors after loading
    if (authLoaded && userLoaded) {
      if (userId && !user) {
        setError('User data could not be loaded. Please try refreshing.')
      }
    }
  }, [authLoaded, userLoaded, userId, user])

  // Error state
  if (error) {
    return (
      <div className="p-8 border border-red-300 rounded-lg bg-red-50">
        <h2 className="text-xl font-bold text-red-800 mb-2">Error</h2>
        <p className="text-red-600">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Reload Page
        </button>
      </div>
    )
  }

  // Loading state
  if (!authLoaded || !userLoaded) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  // Not signed in
  if (!isSignedIn) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p>Please sign in to view your profile</p>
      </div>
    )
  }

  // Display user data
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">User Profile</h1>
      <div className="space-y-2">
        <p><strong>Name:</strong> {user.fullName || 'Not set'}</p>
        <p><strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}</p>
        <p><strong>Username:</strong> {user.username || 'Not set'}</p>
        <p><strong>User ID:</strong> {user.id}</p>
      </div>
    </div>
  )
}

## TypeScript Types Reference