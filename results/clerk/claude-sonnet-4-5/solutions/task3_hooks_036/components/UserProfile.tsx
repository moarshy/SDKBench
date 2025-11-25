'use client'

import { useUser, useAuth, useClerk } from '@clerk/nextjs'
import { SignOutButton } from '@clerk/nextjs'

export default function UserProfile() {
  // useUser hook provides user data and loading state
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()
  
  // useAuth hook provides authentication state
  const { isLoaded: authLoaded } = useAuth()
  
  // useClerk hook provides access to Clerk instance methods
  const { signOut, openUserProfile } = useClerk()

  // Handle loading state
  if (!userLoaded || !authLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading user data...</p>
        </div>
      </div>
    )
  }

  // Handle not signed in state
  if (!isSignedIn) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Not Signed In</h1>
          <p className="text-gray-600">Please sign in to view your profile.</p>
        </div>
      </div>
    )
  }

  // Handle case where user object is not available
  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Error</h1>
          <p className="text-gray-600">Unable to load user data.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6">
          <h1 className="text-3xl font-bold text-white">User Profile</h1>
        </div>

        {/* Profile Content */}
        <div className="p-6">
          {/* Avatar and Basic Info */}
          <div className="flex items-center space-x-6 mb-8">
            {user.imageUrl && (
              <img
                src={user.imageUrl}
                alt={`${user.firstName || 'User'}'s avatar`}
                className="w-24 h-24 rounded-full border-4 border-gray-200"
              />
            )}
            <div>
              <h2 className="text-2xl font-semibold text-gray-800">
                {user.fullName || 'No name provided'}
              </h2>
              <p className="text-gray-600">
                {user.primaryEmailAddress?.emailAddress || 'No email'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                User ID: {user.id}
              </p>
            </div>
          </div>

          {/* Detailed Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-700 mb-2">Personal Information</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-gray-600">First Name:</span>
                  <span className="ml-2 font-medium">{user.firstName || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-gray-600">Last Name:</span>
                  <span className="ml-2 font-medium">{user.lastName || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-gray-600">Username:</span>
                  <span className="ml-2 font-medium">{user.username || 'N/A'}</span>
                </div>
              </div>
            </div>

            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-700 mb-2">Account Details</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-gray-600">Created:</span>
                  <span className="ml-2 font-medium">
                    {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Last Updated:</span>
                  <span className="ml-2 font-medium">
                    {user.updatedAt ? new Date(user.updatedAt).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Email Verified:</span>
                  <span className="ml-2 font-medium">
                    {user.primaryEmailAddress?.verification?.status === 'verified' ? '✓ Yes' : '✗ No'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Email Addresses */}
          {user.emailAddresses && user.emailAddresses.length > 0 && (
            <div className="border rounded-lg p-4 mb-8">
              <h3 className="font-semibold text-gray-700 mb-3">Email Addresses</h3>
              <div className="space-y-2">
                {user.emailAddresses.map((email) => (
                  <div key={email.id} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">{email.emailAddress}</span>
                    <div className="flex items-center space-x-2">
                      {email.id === user.primaryEmailAddress?.id && (
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                          Primary
                        </span>
                      )}
                      {email.verification?.status === 'verified' && (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                          Verified
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Phone Numbers */}
          {user.phoneNumbers && user.phoneNumbers.length > 0 && (
            <div className="border rounded-lg p-4 mb-8">
              <h3 className="font-semibold text-gray-700 mb-3">Phone Numbers</h3>
              <div className="space-y-2">
                {user.phoneNumbers.map((phone) => (
                  <div key={phone.id} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">{phone.phoneNumber}</span>
                    <div className="flex items-center space-x-2">
                      {phone.id === user.primaryPhoneNumber?.id && (
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                          Primary
                        </span>
                      )}
                      {phone.verification?.status === 'verified' && (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                          Verified
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => openUserProfile()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Edit Profile
            </button>
            
            <SignOutButton>
              <button className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg transition-colors">
                Sign Out
              </button>
            </SignOutButton>

            <button
              onClick={() => signOut()}
              className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Sign Out (Programmatic)
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}