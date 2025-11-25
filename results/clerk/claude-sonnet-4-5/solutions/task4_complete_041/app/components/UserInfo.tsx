'use client'

import { useUser } from '@clerk/nextjs'
import { useEffect, useState } from 'react'

export function UserInfo() {
  const { isLoaded, isSignedIn, user } = useUser()
  const [apiData, setApiData] = useState<any>(null)

  useEffect(() => {
    if (isSignedIn) {
      // Fetch data from protected API
      fetch('/api/user')
        .then(res => res.json())
        .then(data => setApiData(data))
        .catch(console.error)
    }
  }, [isSignedIn])

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  if (!isSignedIn) {
    return <div>Please sign in</div>
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="font-semibold">Client-side User Data:</h3>
        <p>Name: {user.firstName} {user.lastName}</p>
        <p>Email: {user.emailAddresses[0]?.emailAddress}</p>
      </div>

      {apiData && (
        <div>
          <h3 className="font-semibold">API Response:</h3>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
            {JSON.stringify(apiData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

### 12. Settings Page Example