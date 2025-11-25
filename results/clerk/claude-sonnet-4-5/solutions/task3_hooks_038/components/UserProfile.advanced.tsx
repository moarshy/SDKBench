'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { SignInButton, SignOutButton } from '@clerk/nextjs'
import { useEffect, useState } from 'react'

export default function UserProfile() {
  const { isLoaded: authLoaded, userId, sessionId } = useAuth()
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Check for any authentication errors
    if (authLoaded && userLoaded && !isSignedIn && !userId) {
      setError('Authentication session expired. Please sign in again.')
    }
  }, [authLoaded, userLoaded, isSignedIn, userId])

  // Handle loading state
  if (!authLoaded || !userLoaded) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading user data...</p>
        </div>
      </div>
    )
  }

  // Handle error state
  if (error) {
    return (
      <div className="max-w-md mx-auto p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-red-800 font-semibold mb-2">Error</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <SignInButton mode="modal">
            <button className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
              Sign In Again
            </button>
          </SignInButton>
        </div>
      </div>
    )
  }

  // Handle unauthenticated state
  if (!isSignedIn || !user) {
    return (
      <div className="max-w-md mx-auto p-8 text-center">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600 mb-6">
          Please sign in to view your profile
        </p>
        <SignInButton mode="modal">
          <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
            Sign In
          </button>
        </SignInButton>
      </div>
    )
  }

  // Display user profile
  return (
    <div className="max-w-2xl mx-auto p-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            {user.imageUrl && (
              <img
                src={user.imageUrl}
                alt={user.fullName || 'User avatar'}
                className="w-16 h-16 rounded-full"
                onError={(e) => {
                  e.currentTarget.src = '/default-avatar.png'
                }}
              />
            )}
            <div>
              <h1 className="text-2xl font-bold">
                {user.fullName || 'User Profile'}
              </h1>
              <p className="text-gray-600">
                {user.primaryEmailAddress?.emailAddress}
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-3 border-t pt-4">
          <ProfileField label="User ID" value={userId || 'N/A'} />
          <ProfileField label="Username" value={user.username || 'Not set'} />
          <ProfileField label="First Name" value={user.firstName || 'Not set'} />
          <ProfileField label="Last Name" value={user.lastName || 'Not set'} />
          <ProfileField
            label="Account Created"
            value={new Date(user.createdAt!).toLocaleDateString()}
          />
        </div>

        <div className="mt-6 pt-6 border-t">
          <SignOutButton>
            <button className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition w-full">
              Sign Out
            </button>
          </SignOutButton>
        </div>
      </div>
    </div>
  )
}

function ProfileField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="font-medium">{value}</p>
    </div>
  )
}

## Usage Example in a Page