'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { SignInButton, SignOutButton } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded: authLoaded, userId, sessionId, signOut } = useAuth()
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()

  // Handle loading state - wait for both auth and user data to load
  if (!authLoaded || !userLoaded) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-20 w-20 bg-gray-200 rounded-full mx-auto"></div>
          <div className="h-4 bg-gray-200 rounded w-48 mx-auto"></div>
          <div className="h-4 bg-gray-200 rounded w-64 mx-auto"></div>
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

  // Display user profile data
  return (
    <div className="max-w-2xl mx-auto p-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-4 mb-6">
          {user.imageUrl && (
            <img
              src={user.imageUrl}
              alt={user.fullName || 'User avatar'}
              className="w-20 h-20 rounded-full"
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

        <div className="space-y-4 border-t pt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">User ID</p>
              <p className="font-mono text-sm">{userId}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Session ID</p>
              <p className="font-mono text-sm truncate">{sessionId}</p>
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-500">Username</p>
            <p className="font-medium">{user.username || 'Not set'}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500">First Name</p>
            <p className="font-medium">{user.firstName || 'Not set'}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500">Last Name</p>
            <p className="font-medium">{user.lastName || 'Not set'}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500">Email Addresses</p>
            <ul className="space-y-1">
              {user.emailAddresses.map((email) => (
                <li key={email.id} className="flex items-center space-x-2">
                  <span className="font-medium">{email.emailAddress}</span>
                  {email.id === user.primaryEmailAddress?.id && (
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      Primary
                    </span>
                  )}
                  {email.verification?.status === 'verified' && (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                      Verified
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {user.phoneNumbers.length > 0 && (
            <div>
              <p className="text-sm text-gray-500">Phone Numbers</p>
              <ul className="space-y-1">
                {user.phoneNumbers.map((phone) => (
                  <li key={phone.id} className="flex items-center space-x-2">
                    <span className="font-medium">{phone.phoneNumber}</span>
                    {phone.id === user.primaryPhoneNumber?.id && (
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        Primary
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div>
            <p className="text-sm text-gray-500">Account Created</p>
            <p className="font-medium">
              {new Date(user.createdAt!).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-500">Last Updated</p>
            <p className="font-medium">
              {new Date(user.updatedAt!).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t flex space-x-4">
          <SignOutButton>
            <button className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition">
              Sign Out
            </button>
          </SignOutButton>
          <button
            onClick={() => user.reload()}
            className="bg-gray-200 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-300 transition"
          >
            Refresh Data
          </button>
        </div>
      </div>
    </div>
  )
}

## Alternative: Minimal Version

If you prefer a simpler implementation without styling: