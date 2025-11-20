'use client'
import { useAuth } from '@clerk/nextjs'

export default function UserProfile() {
  const { isLoaded, isSignedIn, userId } = useAuth()

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  if (!isSignedIn) {
    return <div>Please sign in</div>
  }

  return (
    <div>
      <h1>User Profile</h1>
      <p>User ID: {userId}</p>
    </div>
  )
}
