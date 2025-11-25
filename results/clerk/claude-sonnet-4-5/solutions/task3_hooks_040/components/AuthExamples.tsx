'use client'

import { useAuth, useUser, useClerk } from '@clerk/nextjs'

export function AuthStatusExample() {
  const { isLoaded, isSignedIn, userId } = useAuth()

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <p>Signed In: {isSignedIn ? 'Yes' : 'No'}</p>
      {userId && <p>User ID: {userId}</p>}
    </div>
  )
}

export function SignOutButton() {
  const { signOut } = useClerk()

  return (
    <button onClick={() => signOut()}>
      Sign Out
    </button>
  )
}

export function UserGreeting() {
  const { user } = useUser()

  if (!user) return null

  return (
    <div>
      <p>Hello, {user.firstName || user.username}!</p>
    </div>
  )
}

## Usage Example in a Page