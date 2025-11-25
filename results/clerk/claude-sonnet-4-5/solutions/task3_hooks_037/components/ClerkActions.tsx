'use client'

import { useClerk } from '@clerk/nextjs'

export default function ClerkActions() {
  const { signOut, openSignIn, openUserProfile } = useClerk()

  return (
    <div className="flex gap-2">
      <button
        onClick={() => openSignIn()}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Sign In
      </button>
      <button
        onClick={() => openUserProfile()}
        className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
      >
        Manage Profile
      </button>
      <button
        onClick={() => signOut()}
        className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
      >
        Sign Out
      </button>
    </div>
  )
}

## Usage Example in a Page