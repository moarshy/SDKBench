'use client'

import { useUser, useAuth } from '@clerk/nextjs'

export default function UserProfile() {
  const { user, isLoaded: isUserLoaded } = useUser()
  const { isSignedIn, isLoaded: isAuthLoaded } = useAuth()

  // Handle loading state
  if (!isUserLoaded || !isAuthLoaded) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  // Handle not signed in state
  if (!isSignedIn || !user) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600">Please sign in to view your profile.</p>
      </div>
    )
  }

  // Display user information
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">User Profile</h1>
      
      <div className="bg-white shadow rounded-lg p-6 space-y-4">
        {/* Profile Image */}
        {user.imageUrl && (
          <div className="flex justify-center mb-4">
            <img
              src={user.imageUrl}
              alt={`${user.firstName || 'User'}'s profile`}
              className="w-24 h-24 rounded-full object-cover border-2 border-gray-200"
            />
          </div>
        )}

        {/* User Information */}
        <div className="space-y-3">
          <div>
            <label className="text-sm font-semibold text-gray-600">Full Name</label>
            <p className="text-lg">
              {user.fullName || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-600">First Name</label>
            <p className="text-lg">
              {user.firstName || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-600">Last Name</label>
            <p className="text-lg">
              {user.lastName || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-600">Email</label>
            <p className="text-lg">
              {user.primaryEmailAddress?.emailAddress || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-600">Username</label>
            <p className="text-lg">
              {user.username || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-600">User ID</label>
            <p className="text-sm text-gray-500 font-mono">
              {user.id}
            </p>
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-600">Account Created</label>
            <p className="text-lg">
              {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown'}
            </p>
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-600">Last Sign In</label>
            <p className="text-lg">
              {user.lastSignInAt ? new Date(user.lastSignInAt).toLocaleDateString() : 'Unknown'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

This implementation:

1. **Uses Clerk Hooks**: 
   - `useUser()` to access user data and loading state
   - `useAuth()` to check authentication status

2. **Handles Loading State**: 
   - Shows a skeleton loader while data is being fetched
   - Checks both `isUserLoaded` and `isAuthLoaded` for complete loading state

3. **Handles Error/Unauthenticated State**: 
   - Displays a message when user is not signed in
   - Safely checks for null/undefined user

4. **Displays User Information**: 
   - Profile image with fallback
   - Full name, first name, last name
   - Primary email address
   - Username
   - User ID
   - Account creation date
   - Last sign-in date
   - Uses optional chaining (`?.`) for safe property access

5. **TypeScript Types**: 
   - Clerk hooks provide built-in TypeScript types
   - All user properties are properly typed

6. **Client Component**: 
   - Marked with `'use client'` directive since hooks can only be used in client components

The component is production-ready with proper error handling, loading states, and a clean UI for displaying user profile information.