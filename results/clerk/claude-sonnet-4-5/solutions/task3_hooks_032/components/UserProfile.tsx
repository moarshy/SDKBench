'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { SignInButton, SignOutButton } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded: authLoaded, userId, sessionId, signOut } = useAuth()
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()

  // Handle loading state - wait for both auth and user to load
  if (!authLoaded || !userLoaded) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-pulse">
          <div className="h-8 w-48 bg-gray-200 rounded mb-4"></div>
          <div className="h-4 w-64 bg-gray-200 rounded mb-2"></div>
          <div className="h-4 w-56 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  // Handle unauthenticated state
  if (!isSignedIn || !userId) {
    return (
      <div className="p-8 border rounded-lg shadow-sm">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600 mb-4">
          Please sign in to view your profile
        </p>
        <SignInButton mode="modal">
          <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
            Sign In
          </button>
        </SignInButton>
      </div>
    )
  }

  // Display user information
  return (
    <div className="p-8 border rounded-lg shadow-sm max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">User Profile</h1>
      
      <div className="space-y-4">
        {/* User Avatar */}
        {user.imageUrl && (
          <div className="flex items-center gap-4 mb-6">
            <img
              src={user.imageUrl}
              alt={user.fullName || 'User avatar'}
              className="w-20 h-20 rounded-full border-2 border-gray-200"
            />
            <div>
              <h2 className="text-xl font-semibold">
                {user.fullName || 'Anonymous User'}
              </h2>
              {user.username && (
                <p className="text-gray-600">@{user.username}</p>
              )}
            </div>
          </div>
        )}

        {/* User Details */}
        <div className="bg-gray-50 p-4 rounded-lg space-y-3">
          <div>
            <label className="text-sm font-medium text-gray-500">User ID</label>
            <p className="text-gray-900 font-mono text-sm">{userId}</p>
          </div>

          {user.primaryEmailAddress && (
            <div>
              <label className="text-sm font-medium text-gray-500">Email</label>
              <p className="text-gray-900">
                {user.primaryEmailAddress.emailAddress}
              </p>
              {user.primaryEmailAddress.verification?.status && (
                <span className={`text-xs px-2 py-1 rounded ${
                  user.primaryEmailAddress.verification.status === 'verified'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {user.primaryEmailAddress.verification.status}
                </span>
              )}
            </div>
          )}

          {user.primaryPhoneNumber && (
            <div>
              <label className="text-sm font-medium text-gray-500">Phone</label>
              <p className="text-gray-900">
                {user.primaryPhoneNumber.phoneNumber}
              </p>
            </div>
          )}

          <div>
            <label className="text-sm font-medium text-gray-500">Session ID</label>
            <p className="text-gray-900 font-mono text-sm break-all">
              {sessionId}
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">Created At</label>
            <p className="text-gray-900">
              {new Date(user.createdAt!).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>

          {user.lastSignInAt && (
            <div>
              <label className="text-sm font-medium text-gray-500">Last Sign In</label>
              <p className="text-gray-900">
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

        {/* Additional User Metadata */}
        {user.publicMetadata && Object.keys(user.publicMetadata).length > 0 && (
          <div className="bg-blue-50 p-4 rounded-lg">
            <label className="text-sm font-medium text-gray-700 mb-2 block">
              Public Metadata
            </label>
            <pre className="text-xs bg-white p-2 rounded overflow-auto">
              {JSON.stringify(user.publicMetadata, null, 2)}
            </pre>
          </div>
        )}

        {/* Sign Out Button */}
        <div className="pt-4 border-t">
          <button
            onClick={() => signOut()}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  )
}

## Alternative: Simplified Version