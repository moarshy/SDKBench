'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { SignInButton, SignOutButton } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded: authLoaded, userId } = useAuth()
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()

  // Loading state
  if (!authLoaded || !userLoaded) {
    return <div>Loading...</div>
  }

  // Not signed in
  if (!isSignedIn) {
    return (
      <div>
        <h1>User Profile</h1>
        <p>Please sign in to view your profile</p>
        <SignInButton />
      </div>
    )
  }

  // Signed in - display user data
  return (
    <div>
      <h1>User Profile</h1>
      <p>User ID: {userId}</p>
      <p>Name: {user.fullName}</p>
      <p>Email: {user.primaryEmailAddress?.emailAddress}</p>
      <p>Username: {user.username}</p>
      <SignOutButton />
    </div>
  )
}

## Advanced: With Error Handling