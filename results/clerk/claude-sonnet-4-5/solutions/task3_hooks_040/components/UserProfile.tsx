'use client'

import { useUser } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded, isSignedIn, user } = useUser()

  // Handle loading state
  if (!isLoaded) {
    return (
      <div className="p-6 max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600">Loading user data...</p>
      </div>
    )
  }

  // Handle not signed in state
  if (!isSignedIn) {
    return (
      <div className="p-6 max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600">Please sign in to view your profile.</p>
      </div>
    )
  }

  // Display user information
  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-6">User Profile</h1>
      
      <div className="space-y-4">
        {/* User Avatar */}
        {user.imageUrl && (
          <div className="flex justify-center mb-4">
            <img
              src={user.imageUrl}
              alt={`${user.firstName || 'User'}'s avatar`}
              className="w-24 h-24 rounded-full border-2 border-gray-200"
            />
          </div>
        )}

        {/* User Details */}
        <div className="bg-gray-50 p-4 rounded-lg space-y-3">
          {user.firstName && (
            <div>
              <span className="font-semibold text-gray-700">First Name: </span>
              <span className="text-gray-900">{user.firstName}</span>
            </div>
          )}

          {user.lastName && (
            <div>
              <span className="font-semibold text-gray-700">Last Name: </span>
              <span className="text-gray-900">{user.lastName}</span>
            </div>
          )}

          {user.fullName && (
            <div>
              <span className="font-semibold text-gray-700">Full Name: </span>
              <span className="text-gray-900">{user.fullName}</span>
            </div>
          )}

          {user.primaryEmailAddress && (
            <div>
              <span className="font-semibold text-gray-700">Email: </span>
              <span className="text-gray-900">{user.primaryEmailAddress.emailAddress}</span>
            </div>
          )}

          {user.username && (
            <div>
              <span className="font-semibold text-gray-700">Username: </span>
              <span className="text-gray-900">{user.username}</span>
            </div>
          )}

          <div>
            <span className="font-semibold text-gray-700">User ID: </span>
            <span className="text-gray-900 text-sm break-all">{user.id}</span>
          </div>

          {user.createdAt && (
            <div>
              <span className="font-semibold text-gray-700">Member Since: </span>
              <span className="text-gray-900">
                {new Date(user.createdAt).toLocaleDateString()}
              </span>
            </div>
          )}
        </div>

        {/* Additional User Metadata */}
        {user.publicMetadata && Object.keys(user.publicMetadata).length > 0 && (
          <div className="bg-blue-50 p-4 rounded-lg">
            <h2 className="font-semibold text-gray-700 mb-2">Public Metadata</h2>
            <pre className="text-sm text-gray-900 overflow-auto">
              {JSON.stringify(user.publicMetadata, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}