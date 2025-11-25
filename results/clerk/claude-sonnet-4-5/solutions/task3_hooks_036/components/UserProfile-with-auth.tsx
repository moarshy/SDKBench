'use client'

import { useUser, useAuth } from '@clerk/nextjs'

/**
 * UserProfile component with additional auth state
 * Demonstrates using both useUser and useAuth hooks
 */
export default function UserProfileWithAuth() {
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()
  const { 
    isLoaded: authLoaded, 
    userId, 
    sessionId, 
    getToken 
  } = useAuth()

  if (!userLoaded || !authLoaded) {
    return <div>Loading...</div>
  }

  if (!isSignedIn) {
    return <div>Not signed in</div>
  }

  const handleGetToken = async () => {
    try {
      const token = await getToken()
      console.log('JWT Token:', token)
      alert('Token logged to console')
    } catch (error) {
      console.error('Error getting token:', error)
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">User Profile with Auth</h1>
      
      <div className="space-y-4">
        <section>
          <h2 className="text-xl font-semibold mb-2">User Data (useUser)</h2>
          <div className="bg-gray-100 p-4 rounded">
            <p><strong>Full Name:</strong> {user.fullName}</p>
            <p><strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}</p>
            <p><strong>User ID:</strong> {user.id}</p>
          </div>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">Auth Data (useAuth)</h2>
          <div className="bg-gray-100 p-4 rounded">
            <p><strong>User ID:</strong> {userId}</p>
            <p><strong>Session ID:</strong> {sessionId}</p>
            <button 
              onClick={handleGetToken}
              className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Get JWT Token
            </button>
          </div>
        </section>
      </div>
    </div>
  )
}