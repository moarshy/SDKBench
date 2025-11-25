'use client'

import { useUser, useAuth, SignOutButton } from '@clerk/nextjs'

export default function UserButton() {
  const { isLoaded, isSignedIn, user } = useUser()
  const { signOut } = useAuth()

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  if (!isSignedIn) {
    return <div>Not signed in</div>
  }

  return (
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      gap: '1rem',
      padding: '0.5rem',
      background: '#f8f9fa',
      borderRadius: '0.5rem'
    }}>
      <img 
        src={user.imageUrl} 
        alt={user.firstName || 'User'} 
        style={{ 
          width: '40px', 
          height: '40px', 
          borderRadius: '50%' 
        }}
      />
      <div>
        <div style={{ fontWeight: 'bold' }}>
          {user.firstName} {user.lastName}
        </div>
        <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>
          {user.emailAddresses[0]?.emailAddress}
        </div>
      </div>
      <SignOutButton>
        <button className="btn">Sign Out</button>
      </SignOutButton>
    </div>
  )
}

### 13. Server Action Example