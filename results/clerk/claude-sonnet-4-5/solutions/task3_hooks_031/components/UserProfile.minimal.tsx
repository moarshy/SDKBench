'use client'

import { useUser } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded, isSignedIn, user } = useUser()

  if (!isLoaded) {
    return <div>Loading user data...</div>
  }

  if (!isSignedIn) {
    return <div>Please sign in to view your profile.</div>
  }

  return (
    <div>
      <h1>User Profile</h1>
      <div>
        <p><strong>Name:</strong> {user.fullName || 'Not provided'}</p>
        <p><strong>Username:</strong> {user.username || 'Not set'}</p>
        <p><strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}</p>
        <p><strong>User ID:</strong> {user.id}</p>
      </div>
    </div>
  )
}

## Advanced: With useAuth Hook

For more authentication control: