'use client'

import { useUser } from '@clerk/nextjs'

export function UserInfo() {
  const { isLoaded, isSignedIn, user } = useUser()

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  if (!isSignedIn) {
    return <div>Not signed in</div>
  }

  return (
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="font-semibold mb-2">User Information</h3>
      <div className="space-y-1 text-sm">
        <p><strong>Email:</strong> {user.emailAddresses[0]?.emailAddress}</p>
        <p><strong>Name:</strong> {user.firstName} {user.lastName}</p>
        <p><strong>Username:</strong> {user.username || 'Not set'}</p>
      </div>
    </div>
  )
}

### 13. Settings Page Example