'use client'

import { useUser } from '@clerk/nextjs'

/**
 * Simplified version of UserProfile component
 * Use this if you want a minimal implementation
 */
export default function UserProfileSimple() {
  const { isLoaded, isSignedIn, user } = useUser()

  // Loading state
  if (!isLoaded) {
    return <div>Loading...</div>
  }

  // Not signed in
  if (!isSignedIn) {
    return <div>Please sign in to view your profile.</div>
  }

  // Display user data
  return (
    <div>
      <h1>User Profile</h1>
      <div>
        <p><strong>Name:</strong> {user.fullName}</p>
        <p><strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}</p>
        <p><strong>User ID:</strong> {user.id}</p>
      </div>
    </div>
  )
}