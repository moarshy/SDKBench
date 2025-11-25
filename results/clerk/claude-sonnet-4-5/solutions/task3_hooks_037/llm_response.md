```typescript
// filepath: components/UserProfile.tsx
'use client'

import { useUser } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded, isSignedIn, user } = useUser()

  // Handle loading state
  if (!isLoaded) {
    return (
      <div className="p-6 max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600">Loading user data...</p>
      </div>
    )
  }

  // Handle unauthenticated state
  if (!isSignedIn) {
    return (
      <div className="p-6 max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <p className="text-gray-600">Please sign in to view your profile.</p>
      </div>
    )
  }

  // Display user information
  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">User Profile</h1>
      
      <div className="space-y-4">
        {/* User Avatar */}
        {user.imageUrl && (
          <div className="flex justify-center">
            <img
              src={user.imageUrl}
              alt={`${user.firstName || 'User'}'s avatar`}
              className="w-24 h-24 rounded-full border-2 border-gray-300"
            />
          </div>
        )}

        {/* User Details */}
        <div className="bg-gray-50 p-4 rounded-lg space-y-2">
          {user.firstName && (
            <div>
              <span className="font-semibold">First Name: </span>
              <span>{user.firstName}</span>
            </div>
          )}
          
          {user.lastName && (
            <div>
              <span className="font-semibold">Last Name: </span>
              <span>{user.lastName}</span>
            </div>
          )}
          
          {user.fullName && (
            <div>
              <span className="font-semibold">Full Name: </span>
              <span>{user.fullName}</span>
            </div>
          )}
          
          {user.primaryEmailAddress && (
            <div>
              <span className="font-semibold">Email: </span>
              <span>{user.primaryEmailAddress.emailAddress}</span>
            </div>
          )}
          
          {user.username && (
            <div>
              <span className="font-semibold">Username: </span>
              <span>{user.username}</span>
            </div>
          )}
          
          <div>
            <span className="font-semibold">User ID: </span>
            <span className="text-sm text-gray-600">{user.id}</span>
          </div>
          
          <div>
            <span className="font-semibold">Created: </span>
            <span className="text-sm text-gray-600">
              {new Date(user.createdAt).toLocaleDateString()}
            </span>
          </div>
        </div>

        {/* Phone Numbers */}
        {user.phoneNumbers && user.phoneNumbers.length > 0 && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h2 className="font-semibold mb-2">Phone Numbers</h2>
            <ul className="space-y-1">
              {user.phoneNumbers.map((phone) => (
                <li key={phone.id} className="text-sm">
                  {phone.phoneNumber}
                  {phone.id === user.primaryPhoneNumberId && (
                    <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      Primary
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Email Addresses */}
        {user.emailAddresses && user.emailAddresses.length > 1 && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h2 className="font-semibold mb-2">Email Addresses</h2>
            <ul className="space-y-1">
              {user.emailAddresses.map((email) => (
                <li key={email.id} className="text-sm">
                  {email.emailAddress}
                  {email.id === user.primaryEmailAddressId && (
                    <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      Primary
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
```

This implementation:

1. **Uses the `useUser` hook** from Clerk v5 to access user authentication data
2. **Handles loading state** - Shows a loading message while Clerk initializes
3. **Handles unauthenticated state** - Shows a message when user is not signed in
4. **Displays comprehensive user information**:
   - User avatar/profile image
   - Name fields (first, last, full name)
   - Email address(es)
   - Username
   - User ID
   - Account creation date
   - Phone numbers (if available)
   - Multiple email addresses (if available)
5. **TypeScript-ready** - Works with TypeScript out of the box with Clerk's built-in types
6. **Includes basic styling** - Uses Tailwind CSS classes for a clean presentation
7. **Marks primary contacts** - Shows which email/phone is primary
8. **Client component** - Uses `'use client'` directive as required for hooks in Next.js App Router

The component gracefully handles all three states (loading, unauthenticated, authenticated) and displays relevant information for each scenario.