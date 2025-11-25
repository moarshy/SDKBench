'use client'

import { useUser, useClerk } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded, isSignedIn, user } = useUser()
  const { signOut } = useClerk()

  // Handle loading state
  if (!isLoaded) {
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

  // Handle not signed in state
  if (!isSignedIn) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600">Please sign in to view your profile.</p>
      </div>
    )
  }

  // Handle error state (user should exist if isSignedIn is true)
  if (!user) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-red-600">Error loading user data. Please try again.</p>
      </div>
    )
  }

  // Display user information
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">User Profile</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 space-y-4">
        {/* User Avatar */}
        {user.imageUrl && (
          <div className="flex justify-center mb-4">
            <img
              src={user.imageUrl}
              alt={`${user.firstName || 'User'}'s avatar`}
              className="w-24 h-24 rounded-full border-4 border-gray-200"
            />
          </div>
        )}

        {/* User Details */}
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-600">Full Name</label>
            <p className="text-lg font-semibold">
              {user.fullName || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">First Name</label>
            <p className="text-lg">
              {user.firstName || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Last Name</label>
            <p className="text-lg">
              {user.lastName || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Email</label>
            <p className="text-lg">
              {user.primaryEmailAddress?.emailAddress || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Username</label>
            <p className="text-lg">
              {user.username || 'Not provided'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">User ID</label>
            <p className="text-sm text-gray-500 font-mono">
              {user.id}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Account Created</label>
            <p className="text-lg">
              {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">Last Sign In</label>
            <p className="text-lg">
              {user.lastSignInAt ? new Date(user.lastSignInAt).toLocaleDateString() : 'Unknown'}
            </p>
          </div>
        </div>

        {/* Sign Out Button */}
        <div className="pt-4 border-t">
          <button
            onClick={() => signOut()}
            className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  )
}

This implementation:

1. **Uses Clerk v5 hooks**: 
   - `useUser()` to access user data and authentication state
   - `useClerk()` to access the signOut function

2. **Handles all states properly**:
   - **Loading state**: Shows a skeleton loader while Clerk is initializing
   - **Not signed in**: Displays a message prompting the user to sign in
   - **Error state**: Handles the edge case where user data might not be available
   - **Success state**: Displays comprehensive user information

3. **Displays user information**:
   - Profile image
   - Full name, first name, last name
   - Email address
   - Username
   - User ID
   - Account creation date
   - Last sign-in date

4. **TypeScript types**: Uses Clerk's built-in TypeScript types (automatically inferred from the hooks)

5. **Additional features**:
   - Sign out button for user convenience
   - Clean, accessible UI with proper labels
   - Responsive design with Tailwind CSS classes
   - Handles missing data gracefully with fallback text

The component is marked with `'use client'` directive since it uses React hooks and needs to run on the client side in Next.js 13+ App Router.