'use client';

import { useUser, useAuth, useClerk } from '@clerk/nextjs';
import { SignOutButton } from '@clerk/nextjs';

export default function UserProfile() {
  // useUser hook provides user data and loading state
  const { user, isLoaded: isUserLoaded, isSignedIn } = useUser();
  
  // useAuth hook provides authentication state
  const { isLoaded: isAuthLoaded } = useAuth();
  
  // useClerk hook provides access to Clerk instance methods
  const { signOut, openUserProfile } = useClerk();

  // Handle loading state
  if (!isUserLoaded || !isAuthLoaded) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-pulse">
          <div className="h-20 w-20 bg-gray-200 rounded-full mb-4"></div>
          <div className="h-4 w-32 bg-gray-200 rounded mb-2"></div>
          <div className="h-4 w-48 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  // Handle not signed in state
  if (!isSignedIn || !user) {
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600 mb-4">You need to sign in to view your profile.</p>
        <a 
          href="/sign-in" 
          className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Sign In
        </a>
      </div>
    );
  }

  // Display user information
  return (
    <div className="max-w-2xl mx-auto p-8">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6">
          <h1 className="text-3xl font-bold text-white mb-2">User Profile</h1>
          <p className="text-blue-100">Manage your account information</p>
        </div>

        {/* Profile Content */}
        <div className="p-6">
          {/* Avatar and Basic Info */}
          <div className="flex items-center mb-6 pb-6 border-b">
            <img
              src={user.imageUrl}
              alt={user.fullName || 'User avatar'}
              className="w-20 h-20 rounded-full border-4 border-blue-100"
            />
            <div className="ml-4">
              <h2 className="text-2xl font-semibold text-gray-800">
                {user.fullName || 'No name set'}
              </h2>
              <p className="text-gray-600">
                @{user.username || 'No username'}
              </p>
            </div>
          </div>

          {/* User Details */}
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Email */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-600 mb-1">
                  Primary Email
                </h3>
                <p className="text-gray-800">
                  {user.primaryEmailAddress?.emailAddress || 'No email'}
                </p>
                {user.primaryEmailAddress?.verification?.status === 'verified' && (
                  <span className="inline-block mt-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                    ✓ Verified
                  </span>
                )}
              </div>

              {/* Phone */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-600 mb-1">
                  Primary Phone
                </h3>
                <p className="text-gray-800">
                  {user.primaryPhoneNumber?.phoneNumber || 'No phone number'}
                </p>
              </div>

              {/* User ID */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-600 mb-1">
                  User ID
                </h3>
                <p className="text-gray-800 text-sm font-mono truncate">
                  {user.id}
                </p>
              </div>

              {/* Created At */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-600 mb-1">
                  Member Since
                </h3>
                <p className="text-gray-800">
                  {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>

            {/* Additional Email Addresses */}
            {user.emailAddresses && user.emailAddresses.length > 1 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-600 mb-2">
                  Additional Email Addresses
                </h3>
                <ul className="space-y-1">
                  {user.emailAddresses
                    .filter(email => email.id !== user.primaryEmailAddress?.id)
                    .map(email => (
                      <li key={email.id} className="text-gray-800 text-sm">
                        {email.emailAddress}
                      </li>
                    ))}
                </ul>
              </div>
            )}

            {/* External Accounts */}
            {user.externalAccounts && user.externalAccounts.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-600 mb-2">
                  Connected Accounts
                </h3>
                <div className="flex flex-wrap gap-2">
                  {user.externalAccounts.map(account => (
                    <span
                      key={account.id}
                      className="inline-flex items-center bg-white px-3 py-1 rounded-full text-sm border"
                    >
                      {account.provider}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="mt-6 pt-6 border-t flex flex-wrap gap-3">
            <button
              onClick={() => openUserProfile()}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-medium"
            >
              Edit Profile
            </button>
            
            <SignOutButton>
              <button className="bg-gray-200 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-300 transition font-medium">
                Sign Out
              </button>
            </SignOutButton>

            <button
              onClick={() => signOut()}
              className="bg-red-100 text-red-700 px-6 py-2 rounded-lg hover:bg-red-200 transition font-medium"
            >
              Sign Out (All Devices)
            </button>
          </div>
        </div>
      </div>

      {/* Debug Info (Optional - Remove in production) */}
      <div className="mt-6 bg-gray-100 p-4 rounded-lg">
        <details>
          <summary className="cursor-pointer font-semibold text-gray-700 mb-2">
            Debug: Raw User Data
          </summary>
          <pre className="text-xs overflow-auto bg-white p-4 rounded border">
            {JSON.stringify(user, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}