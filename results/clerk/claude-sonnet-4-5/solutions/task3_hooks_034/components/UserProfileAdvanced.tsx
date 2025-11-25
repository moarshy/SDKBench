'use client'

import { useUser, useAuth, useClerk } from '@clerk/nextjs'
import { useState } from 'react'
import Image from 'next/image'

export default function UserProfileAdvanced() {
  const { isLoaded, isSignedIn, user } = useUser()
  const { signOut } = useClerk()
  const { userId, sessionId } = useAuth()
  const [isSigningOut, setIsSigningOut] = useState(false)

  const handleSignOut = async () => {
    setIsSigningOut(true)
    try {
      await signOut()
    } catch (error) {
      console.error('Error signing out:', error)
      setIsSigningOut(false)
    }
  }

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading user data...</p>
        </div>
      </div>
    )
  }

  if (!isSignedIn || !user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-center max-w-md">
          <h1 className="text-3xl font-bold mb-4">Access Denied</h1>
          <p className="text-gray-600 mb-6">
            Please sign in to view your profile
          </p>
          <a 
            href="/sign-in" 
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Sign In
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">User Profile</h1>
        <button
          onClick={handleSignOut}
          disabled={isSigningOut}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSigningOut ? 'Signing out...' : 'Sign Out'}
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Main Profile Card */}
        <div className="bg-white shadow-lg rounded-lg p-6">
          <div className="flex flex-col items-center text-center">
            {user.imageUrl && (
              <Image
                src={user.imageUrl}
                alt={user.fullName || 'User avatar'}
                width={120}
                height={120}
                className="rounded-full mb-4"
              />
            )}
            <h2 className="text-2xl font-bold mb-2">
              {user.fullName || 'Anonymous User'}
            </h2>
            {user.username && (
              <p className="text-gray-600 mb-4">@{user.username}</p>
            )}
            <div className="w-full space-y-2 text-left">
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Email:</span>
                <span className="font-medium">
                  {user.primaryEmailAddress?.emailAddress || 'N/A'}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Phone:</span>
                <span className="font-medium">
                  {user.primaryPhoneNumber?.phoneNumber || 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Session Information */}
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">Session Information</h3>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">User ID</label>
              <p className="text-gray-900 font-mono text-xs break-all">{userId}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Session ID</label>
              <p className="text-gray-900 font-mono text-xs break-all">{sessionId}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Account Created</label>
              <p className="text-gray-900">
                {new Date(user.createdAt || '').toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Last Active</label>
              <p className="text-gray-900">
                {user.lastSignInAt 
                  ? new Date(user.lastSignInAt).toLocaleString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })
                  : 'Never'}
              </p>
            </div>
          </div>
        </div>

        {/* Additional Details */}
        <div className="bg-white shadow-lg rounded-lg p-6 md:col-span-2">
          <h3 className="text-xl font-bold mb-4">Additional Details</h3>
          
          {/* Email Addresses */}
          {user.emailAddresses && user.emailAddresses.length > 0 && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-700 mb-2">Email Addresses</h4>
              <ul className="space-y-2">
                {user.emailAddresses.map((email) => (
                  <li key={email.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span className="text-gray-900">{email.emailAddress}</span>
                    <div className="flex items-center space-x-2">
                      {email.verification?.status === 'verified' && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          ✓ Verified
                        </span>
                      )}
                      {email.id === user.primaryEmailAddress?.id && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          Primary
                        </span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Phone Numbers */}
          {user.phoneNumbers && user.phoneNumbers.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Phone Numbers</h4>
              <ul className="space-y-2">
                {user.phoneNumbers.map((phone) => (
                  <li key={phone.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span className="text-gray-900">{phone.phoneNumber}</span>
                    <div className="flex items-center space-x-2">
                      {phone.verification?.status === 'verified' && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          ✓ Verified
                        </span>
                      )}
                      {phone.id === user.primaryPhoneNumber?.id && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          Primary
                        </span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Public Metadata */}
          {user.publicMetadata && Object.keys(user.publicMetadata).length > 0 && (
            <div className="mt-6">
              <h4 className="font-semibold text-gray-700 mb-2">Public Metadata</h4>
              <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto">
                {JSON.stringify(user.publicMetadata, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

## TypeScript Type Definitions