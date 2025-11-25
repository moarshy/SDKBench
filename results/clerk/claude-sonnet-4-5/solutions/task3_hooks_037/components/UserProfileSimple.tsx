'use client'

import { useUser } from '@clerk/nextjs'

export default function UserProfileSimple() {
  const { isLoaded, isSignedIn, user } = useUser()

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  if (!isSignedIn) {
    return <div>Please sign in to view your profile.</div>
  }

  return (
    <div>
      <h1>User Profile</h1>
      <div>
        <p><strong>Name:</strong> {user.fullName}</p>
        <p><strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}</p>
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>User ID:</strong> {user.id}</p>
      </div>
    </div>
  )
}

## Additional Hook Examples

### Using useAuth Hook