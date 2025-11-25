'use client'

import { useUser, useAuth } from '@clerk/nextjs'
import { useEffect, useState } from 'react'

export default function UserInfo() {
  const { isLoaded, isSignedIn, user } = useUser()
  const { getToken } = useAuth()
  const [apiData, setApiData] = useState<any>(null)

  useEffect(() => {
    async function fetchData() {
      if (isSignedIn) {
        try {
          const token = await getToken()
          const response = await fetch('/api/user', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          })
          const data = await response.json()
          setApiData(data)
        } catch (error) {
          console.error('Error fetching data:', error)
        }
      }
    }

    fetchData()
  }, [isSignedIn, getToken])

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  if (!isSignedIn) {
    return <div>Please sign in</div>
  }

  return (
    <div className="p-4 border rounded-lg">
      <h3 className="font-semibold mb-2">Client-Side User Info</h3>
      <p className="text-sm">Name: {user.fullName}</p>
      <p className="text-sm">Email: {user.primaryEmailAddress?.emailAddress}</p>
      
      {apiData && (
        <div className="mt-4 p-2 bg-gray-100 rounded">
          <p className="text-xs font-mono">API Response:</p>
          <pre className="text-xs">{JSON.stringify(apiData, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}

### 12. Server Action Example