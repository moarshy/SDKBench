'use client'

import { useUser } from '@clerk/nextjs'
import Image from 'next/image'

export default function UserProfile() {
  const { isLoaded, isSignedIn, user } = useUser()

  // Loading state - while Clerk is initializing
  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-pulse space-y-4 w-full max-w-md">
          <div className="h-24 w-24 bg-gray-200 rounded-full mx-auto"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
        </div>
      </div>
    )
  }

  // Not signed in state
  if (!isSignedIn) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 max-w-md">
          <h2 className="text-xl font-semibold text-yellow-800 mb-2">
            Not Signed In
          </h2>
          <p className="text-yellow-700">
            Please sign in to view your profile information.
          </p>
        </div>
      </div>
    )
  }

  // User is signed in - display profile
  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        {/* Header Section */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 h-32"></div>
        
        {/* Profile Content */}
        <div className="relative px-6 pb-6">
          {/* Profile Image */}
          <div className="flex justify-center -mt-16 mb-4">
            {user.imageUrl ? (
              <Image
                src={user.imageUrl}
                alt={user.fullName || 'User profile'}
                width={128}
                height={128}
                className="rounded-full border-4 border-white shadow-lg"
              />
            ) : (
              <div className="w-32 h-32 rounded-full border-4 border-white shadow-lg bg-gray-200 flex items-center justify-center">
                <span className="text-4xl text-gray-500">
                  {user.firstName?.[0] || user.username?.[0] || '?'}
                </span>
              </div>
            )}
          </div>

          {/* User Information */}
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-1">
              {user.fullName || user.username || 'Anonymous User'}
            </h1>
            {user.username && (
              <p className="text-gray-600">@{user.username}</p>
            )}
          </div>

          {/* Details Grid */}
          <div className="space-y-4">
            {/* Email Addresses */}
            {user.emailAddresses && user.emailAddresses.length > 0 && (
              <div className="border-t pt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  Email Addresses
                </h3>
                <div className="space-y-2">
                  {user.emailAddresses.map((email) => (
                    <div
                      key={email.id}
                      className="flex items-center justify-between bg-gray-50 p-3 rounded-lg"
                    >
                      <span className="text-gray-900">{email.emailAddress}</span>
                      <div className="flex gap-2">
                        {email.verification?.status === 'verified' && (
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                            Verified
                          </span>
                        )}
                        {email.id === user.primaryEmailAddressId && (
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                            Primary
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
              <div className="border-t pt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  Phone Numbers
                </h3>
                <div className="space-y-2">
                  {user.phoneNumbers.map((phone) => (
                    <div
                      key={phone.id}
                      className="flex items-center justify-between bg-gray-50 p-3 rounded-lg"
                    >
                      <span className="text-gray-900">{phone.phoneNumber}</span>
                      <div className="flex gap-2">
                        {phone.verification?.status === 'verified' && (
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                            Verified
                          </span>
                        )}
                        {phone.id === user.primaryPhoneNumberId && (
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                            Primary
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Additional Information */}
            <div className="border-t pt-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                Account Information
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">User ID</p>
                  <p className="text-sm text-gray-900 font-mono truncate">
                    {user.id}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Created</p>
                  <p className="text-sm text-gray-900">
                    {user.createdAt
                      ? new Date(user.createdAt).toLocaleDateString()
                      : 'N/A'}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Last Sign In</p>
                  <p className="text-sm text-gray-900">
                    {user.lastSignInAt
                      ? new Date(user.lastSignInAt).toLocaleDateString()
                      : 'N/A'}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Two-Factor</p>
                  <p className="text-sm text-gray-900">
                    {user.twoFactorEnabled ? 'Enabled' : 'Disabled'}
                  </p>
                </div>
              </div>
            </div>

            {/* External Accounts */}
            {user.externalAccounts && user.externalAccounts.length > 0 && (
              <div className="border-t pt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  Connected Accounts
                </h3>
                <div className="flex flex-wrap gap-2">
                  {user.externalAccounts.map((account) => (
                    <div
                      key={account.id}
                      className="bg-gray-50 px-3 py-2 rounded-lg flex items-center gap-2"
                    >
                      <span className="text-sm text-gray-900 capitalize">
                        {account.provider}
                      </span>
                      {account.verification?.status === 'verified' && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                          ✓
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

## Alternative: Simplified Version

If you prefer a simpler implementation without all the styling: