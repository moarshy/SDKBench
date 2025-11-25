```typescript
// filepath: components/UserProfile.tsx
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
          <h1 className="text-2xl font-bold mb-4">Loading...</h1>
          <p className="text-gray-600">Fetching user data...</p>
        </div>
      </div>
    )
  }

  // Handle not signed in state
  if (!isSignedIn || !user) {
    return (
      <div className="p-8 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h1 className="text-2xl font-bold mb-4 text-yellow-800">Not Signed In</h1>
        <p className="text-yellow-700">Please sign in to view your profile.</p>
      </div>
    )
  }

  // Display user information
  return (
    <div className="p-8 bg-white shadow-lg rounded-lg max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">User Profile</h1>
      
      <div className="space-y-4">
        {/* User Avatar */}
        {user.imageUrl && (
          <div className="flex items-center mb-6">
            <img
              src={user.imageUrl}
              alt={user.fullName || 'User avatar'}
              className="w-20 h-20 rounded-full border-2 border-gray-300"
            />
          </div>
        )}

        {/* User Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600 font-semibold mb-1">Full Name</p>
            <p className="text-lg text-gray-900">{user.fullName || 'Not provided'}</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600 font-semibold mb-1">Username</p>
            <p className="text-lg text-gray-900">{user.username || 'Not set'}</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600 font-semibold mb-1">Email</p>
            <p className="text-lg text-gray-900">
              {user.primaryEmailAddress?.emailAddress || 'No email'}
            </p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600 font-semibold mb-1">User ID</p>
            <p className="text-lg text-gray-900 font-mono text-sm break-all">{user.id}</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600 font-semibold mb-1">First Name</p>
            <p className="text-lg text-gray-900">{user.firstName || 'Not provided'}</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600 font-semibold mb-1">Last Name</p>
            <p className="text-lg text-gray-900">{user.lastName || 'Not provided'}</p>
          </div>
        </div>

        {/* Additional Information */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Account Information</h2>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Email Verified:</span>
              <span className={`font-semibold ${user.primaryEmailAddress?.verification?.status === 'verified' ? 'text-green-600' : 'text-yellow-600'}`}>
                {user.primaryEmailAddress?.verification?.status === 'verified' ? 'Yes' : 'No'}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-gray-600">Created At:</span>
              <span className="font-semibold text-gray-900">
                {new Date(user.createdAt || '').toLocaleDateString()}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-gray-600">Last Sign In:</span>
              <span className="font-semibold text-gray-900">
                {user.lastSignInAt ? new Date(user.lastSignInAt).toLocaleDateString() : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
```