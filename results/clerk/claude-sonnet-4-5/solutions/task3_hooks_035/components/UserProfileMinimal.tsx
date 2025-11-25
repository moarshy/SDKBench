'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { SignInButton, SignOutButton } from '@clerk/nextjs'

export default function UserProfileMinimal() {
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
      <div>
        <p><strong>User ID:</strong> {userId}</p>
        <p><strong>Name:</strong> {user.fullName}</p>
        <p><strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}</p>
        <p><strong>Username:</strong> {user.username}</p>
        {user.imageUrl && (
          <img src={user.imageUrl} alt="Profile" width={100} height={100} />
        )}
      </div>
      <SignOutButton />
    </div>
  )
}

## Advanced: With Error Handling