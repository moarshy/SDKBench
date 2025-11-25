'use client'

import { useUser, useAuth } from '@clerk/nextjs'

export default function UserInfo() {
  const { isLoaded, isSignedIn, user } = useUser()
  const { signOut } = useAuth()

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  if (!isSignedIn) {
    return <div>Please sign in</div>
  }

  return (
    <div className="card" style={{ marginTop: '2rem' }}>
      <h3>Client-Side User Info</h3>
      <p style={{ marginTop: '1rem' }}>
        <strong>Email:</strong> {user.emailAddresses[0]?.emailAddress}
      </p>
      <p>
        <strong>Name:</strong> {user.firstName} {user.lastName}
      </p>
      <button
        onClick={() => signOut()}
        style={{
          marginTop: '1rem',
          padding: '0.5rem 1rem',
          backgroundColor: '#dc3545',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
        }}
      >
        Sign Out
      </button>
    </div>
  )
}

### 13. API Route with POST Example