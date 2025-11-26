'use client'

import { useUser } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded, isSignedIn, user } = useUser()

  // Handle loading state
  if (!isLoaded) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  // Handle not signed in state
  if (!isSignedIn) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600">Please sign in to view your profile.</p>
      </div>
    )
  }

  // Display user information
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">User Profile</h1>
      
      <div className="bg-white shadow rounded-lg p-6 space-y-4">
        {/* User Avatar */}
        {user.imageUrl && (
          <div className="flex justify-center mb-4">
            <img
              src={user.imageUrl}
              alt={user.fullName || 'User avatar'}
              className="w-24 h-24 rounded-full border-2 border-gray-200"
            />
          </div>
        )}

        {/* User Details */}
        <div className="space-y-3">
          {user.fullName && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Full Name</label>
              <p className="mt-1 text-gray-900">{user.fullName}</p>
            </div>
          )}

          {user.primaryEmailAddress && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <p className="mt-1 text-gray-900">{user.primaryEmailAddress.emailAddress}</p>
            </div>
          )}

          {user.username && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Username</label>
              <p className="mt-1 text-gray-900">@{user.username}</p>
            </div>
          )}

          {user.primaryPhoneNumber && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Phone</label>
              <p className="mt-1 text-gray-900">{user.primaryPhoneNumber.phoneNumber}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">User ID</label>
            <p className="mt-1 text-gray-900 text-sm font-mono">{user.id}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Account Created</label>
            <p className="mt-1 text-gray-900">
              {new Date(user.createdAt).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </p>
          </div>

          {user.lastSignInAt && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Last Sign In</label>
              <p className="mt-1 text-gray-900">
                {new Date(user.lastSignInAt).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}