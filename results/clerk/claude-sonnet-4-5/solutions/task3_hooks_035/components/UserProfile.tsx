'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { SignInButton, SignOutButton } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded: authLoaded, userId, sessionId, signOut } = useAuth()
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()

  // Handle loading state
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
  if (!isSignedIn || !user) {
    return (
      <div className="p-8 max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <p className="text-yellow-800">
            You need to sign in to view your profile.
          </p>
        </div>
        <SignInButton mode="modal">
          <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            Sign In
          </button>
        </SignInButton>
      </div>
    )
  }

  // Display user profile
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6">
          <div className="flex items-center space-x-4">
            {user.imageUrl && (
              <img
                src={user.imageUrl}
                alt={user.fullName || 'User avatar'}
                className="w-20 h-20 rounded-full border-4 border-white shadow-lg"
              />
            )}
            <div className="text-white">
              <h1 className="text-3xl font-bold">
                {user.fullName || 'User Profile'}
              </h1>
              <p className="text-blue-100">
                {user.primaryEmailAddress?.emailAddress}
              </p>
            </div>
          </div>
        </div>

        {/* User Information */}
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* User ID */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-600 mb-1">
                User ID
              </h3>
              <p className="text-gray-900 font-mono text-sm break-all">
                {userId}
              </p>
            </div>

            {/* Session ID */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-600 mb-1">
                Session ID
              </h3>
              <p className="text-gray-900 font-mono text-sm break-all">
                {sessionId}
              </p>
            </div>

            {/* Username */}
            {user.username && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-600 mb-1">
                  Username
                </h3>
                <p className="text-gray-900">@{user.username}</p>
              </div>
            )}

            {/* First Name */}
            {user.firstName && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-600 mb-1">
                  First Name
                </h3>
                <p className="text-gray-900">{user.firstName}</p>
              </div>
            )}

            {/* Last Name */}
            {user.lastName && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-600 mb-1">
                  Last Name
                </h3>
                <p className="text-gray-900">{user.lastName}</p>
              </div>
            )}

            {/* Created At */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-600 mb-1">
                Member Since
              </h3>
              <p className="text-gray-900">
                {new Date(user.createdAt!).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
          </div>

          {/* Email Addresses */}
          {user.emailAddresses && user.emailAddresses.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">
                Email Addresses
              </h3>
              <ul className="space-y-2">
                {user.emailAddresses.map((email) => (
                  <li
                    key={email.id}
                    className="flex items-center justify-between"
                  >
                    <span className="text-gray-900">{email.emailAddress}</span>
                    {email.id === user.primaryEmailAddressId && (
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        Primary
                      </span>
                    )}
                    {email.verification?.status === 'verified' && (
                      <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                        Verified
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Phone Numbers */}
          {user.phoneNumbers && user.phoneNumbers.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">
                Phone Numbers
              </h3>
              <ul className="space-y-2">
                {user.phoneNumbers.map((phone) => (
                  <li
                    key={phone.id}
                    className="flex items-center justify-between"
                  >
                    <span className="text-gray-900">{phone.phoneNumber}</span>
                    {phone.id === user.primaryPhoneNumberId && (
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        Primary
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex space-x-4 pt-4">
            <SignOutButton>
              <button className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors">
                Sign Out
              </button>
            </SignOutButton>
          </div>
        </div>
      </div>
    </div>
  )
}

## Alternative: Minimal Version

If you prefer a simpler implementation without extensive styling: