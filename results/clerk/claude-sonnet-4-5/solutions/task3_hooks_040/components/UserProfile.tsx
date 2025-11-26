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
        {/* Profile Image */}
        {user.imageUrl && (
          <div className="flex justify-center mb-4">
            <img
              src={user.imageUrl}
              alt={`${user.firstName || 'User'}'s profile`}
              className="w-24 h-24 rounded-full border-2 border-gray-200"
            />
          </div>
        )}

        {/* User Details */}
        <div className="space-y-3">
          {user.fullName && (
            <div>
              <label className="text-sm font-semibold text-gray-600">Full Name</label>
              <p className="text-lg">{user.fullName}</p>
            </div>
          )}

          {user.firstName && (
            <div>
              <label className="text-sm font-semibold text-gray-600">First Name</label>
              <p className="text-lg">{user.firstName}</p>
            </div>
          )}

          {user.lastName && (
            <div>
              <label className="text-sm font-semibold text-gray-600">Last Name</label>
              <p className="text-lg">{user.lastName}</p>
            </div>
          )}

          {user.primaryEmailAddress && (
            <div>
              <label className="text-sm font-semibold text-gray-600">Email</label>
              <p className="text-lg">{user.primaryEmailAddress.emailAddress}</p>
            </div>
          )}

          {user.username && (
            <div>
              <label className="text-sm font-semibold text-gray-600">Username</label>
              <p className="text-lg">@{user.username}</p>
            </div>
          )}

          <div>
            <label className="text-sm font-semibold text-gray-600">User ID</label>
            <p className="text-sm text-gray-500 font-mono">{user.id}</p>
          </div>

          {user.createdAt && (
            <div>
              <label className="text-sm font-semibold text-gray-600">Member Since</label>
              <p className="text-lg">
                {new Date(user.createdAt).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}