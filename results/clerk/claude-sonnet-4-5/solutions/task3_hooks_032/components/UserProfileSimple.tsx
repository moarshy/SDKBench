'use client'

import { useAuth, useUser } from '@clerk/nextjs'

export default function UserProfileSimple() {
  const { isLoaded, isSignedIn, user } = useUser()

  // Loading state
  if (!isLoaded) {
    return <div>Loading user data...</div>
  }

  // Not signed in
  if (!isSignedIn) {
    return <div>Please sign in to view your profile</div>
  }

  // Display user data
  return (
    <div>
      <h1>User Profile</h1>
      <p>Welcome, {user.fullName || user.username || 'User'}!</p>
      <p>Email: {user.primaryEmailAddress?.emailAddress}</p>
      <p>User ID: {user.id}</p>
    </div>
  )
}

## Advanced: With Error Boundary