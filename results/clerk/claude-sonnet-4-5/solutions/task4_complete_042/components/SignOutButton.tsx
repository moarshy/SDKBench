'use client'

import { useClerk } from '@clerk/nextjs'
import { useRouter } from 'next/navigation'

export function SignOutButton() {
  const { signOut } = useClerk()
  const router = useRouter()

  const handleSignOut = async () => {
    await signOut()
    router.push('/')
  }

  return (
    <button
      onClick={handleSignOut}
      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
    >
      Sign Out
    </button>
  )
}

### 10. Protected API Route