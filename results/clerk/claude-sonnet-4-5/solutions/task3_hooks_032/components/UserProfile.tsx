'use client'

import { useUser, useAuth } from '@clerk/nextjs'

export default function UserProfile() {
  const { user, isLoaded: isUserLoaded } = useUser()
  const { isSignedIn, isLoaded: isAuthLoaded } = useAuth()

  // Handle loading state
  if (!isUserLoaded || !isAuthLoaded) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-pulse">
          <h1 className="text-2xl font-bold mb-4">User Profile</h1>
          <p className="text-gray-600">Loading user data...</p>
        </div>
      </div>
    )
  }

  // Handle not signed in state
  if (!isSignedIn || !user) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600">Please sign in to view your profile.</p>
      </div>
    )
  }

  // Display user information
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">User Profile</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 space-y-4">
        {/* Profile Image */}
        {user.imageUrl && (
          <div className="flex justify-center mb-4">
            <img
              src={user.imageUrl}
              alt={`${user.firstName || 'User'}'s profile`}
              className="w-24 h-24 rounded-full border-4 border-gray-200"
            />
          </div>
        )}

        {/* User Details */}
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">Full Name</label>
            <p className="mt-1 text-lg">
              {user.fullName || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">First Name</label>
            <p className="mt-1 text-lg">
              {user.firstName || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Last Name</label>
            <p className="mt-1 text-lg">
              {user.lastName || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <p className="mt-1 text-lg">
              {user.primaryEmailAddress?.emailAddress || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Username</label>
            <p className="mt-1 text-lg">
              {user.username || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">User ID</label>
            <p className="mt-1 text-sm text-gray-600 font-mono">
              {user.id}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Account Created</label>
            <p className="mt-1 text-lg">
              {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown'}
            </p>
          </div>

          {/* Email Verification Status */}
          {user.primaryEmailAddress && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Email Verified</label>
              <p className="mt-1">
                <span
                  className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                    user.primaryEmailAddress.verification?.status === 'verified'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {user.primaryEmailAddress.verification?.status === 'verified'
                    ? '✓ Verified'
                    : '⚠ Not Verified'}
                </span>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}