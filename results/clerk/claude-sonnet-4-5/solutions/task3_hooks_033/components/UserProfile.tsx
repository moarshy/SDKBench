'use client';

import { useUser, useClerk } from '@clerk/nextjs';
import { SignOutButton } from '@clerk/nextjs';

export default function UserProfile() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { signOut } = useClerk();

  // Handle loading state
  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-pulse">
          <div className="h-20 w-20 bg-gray-200 rounded-full mb-4"></div>
          <div className="h-4 w-48 bg-gray-200 rounded mb-2"></div>
          <div className="h-4 w-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  // Handle not signed in state
  if (!isSignedIn) {
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600 mb-4">You are not signed in.</p>
        <a
          href="/sign-in"
          className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Sign In
        </a>
      </div>
    );
  }

  // Handle error state (user should exist if isSignedIn is true)
  if (!user) {
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-bold mb-4">Error</h1>
        <p className="text-red-600">Unable to load user data. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">User Profile</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 space-y-4">
        {/* Profile Image */}
        <div className="flex items-center space-x-4">
          {user.imageUrl && (
            <img
              src={user.imageUrl}
              alt={`${user.firstName || 'User'}'s profile`}
              className="w-20 h-20 rounded-full object-cover"
            />
          )}
          <div>
            <h2 className="text-2xl font-semibold">
              {user.firstName} {user.lastName}
            </h2>
            {user.username && (
              <p className="text-gray-600">@{user.username}</p>
            )}
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

          {user.primaryPhoneNumber && (
            <div>
              <label className="text-sm font-medium text-gray-500">Phone</label>
              <p className="text-gray-900">
                {user.primaryPhoneNumber.phoneNumber}
              </p>
            </div>
          )}

          <div>
            <label className="text-sm font-medium text-gray-500">User ID</label>
            <p className="text-gray-900 font-mono text-sm">{user.id}</p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">
              Account Created
            </label>
            <p className="text-gray-900">
              {new Date(user.createdAt).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">
              Last Sign In
            </label>
            <p className="text-gray-900">
              {user.lastSignInAt
                ? new Date(user.lastSignInAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })
                : 'N/A'}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="border-t pt-4 flex gap-3">
          <SignOutButton>
            <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
              Sign Out
            </button>
          </SignOutButton>
          
          <button
            onClick={() => window.location.href = '/user-profile'}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
          >
            Manage Account
          </button>
        </div>
      </div>
    </div>
  );
}

## Alternative: More Advanced Version with useAuth Hook