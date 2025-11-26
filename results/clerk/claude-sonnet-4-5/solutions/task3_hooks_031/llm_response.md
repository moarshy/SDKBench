```typescript
// filepath: components/UserProfile.tsx
'use client'

import { useUser } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded, isSignedIn, user } = useUser()

  // Handle loading state
  if (!isLoaded) {
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
  if (!isSignedIn) {
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
              className="w-24 h-24 rounded-full border-2 border-gray-200"
            />
          </div>
        )}

        {/* User Details */}
        <div className="space-y-3">
          {user.fullName && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Full Name</label>
              <p className="mt-1 text-gray-900">{user.fullName}</p>
            </div>
          )}

          {user.firstName && (
            <div>
              <label className="block text-sm font-medium text-gray-700">First Name</label>
              <p className="mt-1 text-gray-900">{user.firstName}</p>
            </div>
          )}

          {user.lastName && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Last Name</label>
              <p className="mt-1 text-gray-900">{user.lastName}</p>
            </div>
          )}

          {user.primaryEmailAddress && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <p className="mt-1 text-gray-900">{user.primaryEmailAddress.emailAddress}</p>
            </div>
          )}

          {user.primaryPhoneNumber && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Phone</label>
              <p className="mt-1 text-gray-900">{user.primaryPhoneNumber.phoneNumber}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">User ID</label>
            <p className="mt-1 text-gray-900 font-mono text-sm">{user.id}</p>
          </div>

          {user.username && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Username</label>
              <p className="mt-1 text-gray-900">@{user.username}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">Account Created</label>
            <p className="mt-1 text-gray-900">
              {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Last Updated</label>
            <p className="mt-1 text-gray-900">
              {user.updatedAt ? new Date(user.updatedAt).toLocaleDateString() : 'N/A'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
```

This implementation:

1. **Uses the `useUser` hook** from `@clerk/nextjs` to access user authentication data
2. **Handles loading state** with a skeleton loader while Clerk initializes
3. **Handles not signed in state** with a friendly message
4. **Displays comprehensive user information** including:
   - Profile image
   - Full name, first name, last name
   - Primary email address
   - Primary phone number (if available)
   - User ID
   - Username (if set)
   - Account creation and update dates
5. **Uses TypeScript** with proper typing from Clerk's types
6. **Includes the 'use client' directive** since hooks can only be used in client components
7. **Has proper styling** with Tailwind CSS classes for a clean UI
8. **Safely handles optional fields** with conditional rendering

The component is production-ready and follows Next.js 13+ App Router conventions with Clerk v5.