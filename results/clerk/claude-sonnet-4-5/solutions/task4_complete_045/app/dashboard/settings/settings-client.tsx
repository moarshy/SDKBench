'use client'

import { useUser, useAuth } from '@clerk/nextjs'
import { useState } from 'react'

export default function SettingsClient() {
  const { user, isLoaded } = useUser()
  const { signOut } = useAuth()
  const [showConfirm, setShowConfirm] = useState(false)

  if (!isLoaded) {
    return <div>Loading...</div>
  }

  const handleSignOut = async () => {
    await signOut()
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Account Settings</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <p className="text-gray-900">
              {user?.emailAddresses[0]?.emailAddress}
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name
            </label>
            <p className="text-gray-900">
              {user?.firstName} {user?.lastName}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Danger Zone</h2>
        <div className="space-y-4">
          {!showConfirm ? (
            <button
              onClick={() => setShowConfirm(true)}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Sign Out
            </button>
          ) : (
            <div className="space-y-2">
              <p className="text-gray-700">Are you sure you want to sign out?</p>
              <div className="flex gap-2">
                <button
                  onClick={handleSignOut}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Yes, Sign Out
                </button>
                <button
                  onClick={() => setShowConfirm(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

### 10. Protected API Route