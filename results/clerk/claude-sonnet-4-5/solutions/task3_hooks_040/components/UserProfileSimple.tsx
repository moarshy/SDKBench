'use client'

import { useUser } from '@clerk/nextjs'

export default function UserProfileSimple() {
  const { isLoaded, isSignedIn, user } = useUser()

  if (!isLoaded) {
    return <div>Loading user data...</div>
  }

  if (!isSignedIn) {
    return <div>Please sign in to view your profile.</div>
  }

  return (
    <div>
      <h1>User Profile</h1>
      
      <div>
        <h2>Basic Information</h2>
        <p><strong>Name:</strong> {user.fullName || 'Not provided'}</p>
        <p><strong>Username:</strong> {user.username || 'Not provided'}</p>
        <p><strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}</p>
        <p><strong>User ID:</strong> {user.id}</p>
      </div>

      {user.imageUrl && (
        <div>
          <h2>Profile Picture</h2>
          <img src={user.imageUrl} alt="Profile" width={100} height={100} />
        </div>
      )}

      <div>
        <h2>Account Details</h2>
        <p><strong>Created:</strong> {new Date(user.createdAt!).toLocaleString()}</p>
        <p><strong>Last Sign In:</strong> {user.lastSignInAt ? new Date(user.lastSignInAt).toLocaleString() : 'N/A'}</p>
        <p><strong>Two-Factor Enabled:</strong> {user.twoFactorEnabled ? 'Yes' : 'No'}</p>
      </div>
    </div>
  )
}

## Additional Hook Examples