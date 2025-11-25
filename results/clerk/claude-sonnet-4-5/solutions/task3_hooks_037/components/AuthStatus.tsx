'use client'

import { useAuth } from '@clerk/nextjs'

export default function AuthStatus() {
  const { isLoaded, userId, sessionId, getToken } = useAuth()

  if (!isLoaded) {
    return <div>Loading auth status...</div>
  }

  const handleGetToken = async () => {
    try {
      const token = await getToken()
      console.log('JWT Token:', token)
    } catch (error) {
      console.error('Error getting token:', error)
    }
  }

  return (
    <div className="p-4 border rounded">
      <h2 className="text-xl font-bold mb-2">Auth Status</h2>
      <p>User ID: {userId || 'Not signed in'}</p>
      <p>Session ID: {sessionId || 'No active session'}</p>
      {userId && (
        <button
          onClick={handleGetToken}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
        >
          Get JWT Token
        </button>
      )}
    </div>
  )
}

### Using useClerk Hook