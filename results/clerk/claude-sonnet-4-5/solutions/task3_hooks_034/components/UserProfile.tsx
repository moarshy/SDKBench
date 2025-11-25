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
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600 mb-4">You need to sign in to view your profile</p>
        <a 
          href="/sign-in" 
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
        >
          Sign In
        </a>
      </div>
    )
  }

  // Signed in - display user data
  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">User Profile</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 space-y-6">
        {/* Profile Image */}
        <div className="flex items-center space-x-4">
          {user.imageUrl && (
            <Image
              src={user.imageUrl}
              alt={user.fullName || 'User avatar'}
              width={80}
              height={80}
              className="rounded-full"
            />
          )}
          <div>
            <h2 className="text-2xl font-semibold">
              {user.fullName || 'No name set'}
            </h2>
            <p className="text-gray-600">@{user.username || 'No username'}</p>
          </div>
        </div>

        {/* User Information */}
        <div className="border-t pt-4 space-y-3">
          <div>
            <label className="text-sm font-medium text-gray-500">Email</label>
            <p className="text-gray-900">
              {user.primaryEmailAddress?.emailAddress || 'No email'}
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">Phone</label>
            <p className="text-gray-900">
              {user.primaryPhoneNumber?.phoneNumber || 'No phone number'}
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">User ID</label>
            <p className="text-gray-900 font-mono text-sm">{user.id}</p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">Created</label>
            <p className="text-gray-900">
              {new Date(user.createdAt || '').toLocaleDateString()}
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">Last Sign In</label>
            <p className="text-gray-900">
              {user.lastSignInAt 
                ? new Date(user.lastSignInAt).toLocaleString()
                : 'Never'}
            </p>
          </div>
        </div>

        {/* Email Addresses */}
        {user.emailAddresses && user.emailAddresses.length > 0 && (
          <div className="border-t pt-4">
            <label className="text-sm font-medium text-gray-500 block mb-2">
              All Email Addresses
            </label>
            <ul className="space-y-2">
              {user.emailAddresses.map((email) => (
                <li key={email.id} className="flex items-center space-x-2">
                  <span className="text-gray-900">{email.emailAddress}</span>
                  {email.verification?.status === 'verified' && (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                      Verified
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

## Advanced Example with Multiple Hooks