'use client'
import { useClerk } from '@clerk/nextjs'

export default function UserProfile() {
  const { user, signOut } = useClerk()

  if (!user) {
    return <div>Please sign in</div>
  }

  return (
    <div>
      <h1>Welcome, {user.firstName}!</h1>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  )
}
