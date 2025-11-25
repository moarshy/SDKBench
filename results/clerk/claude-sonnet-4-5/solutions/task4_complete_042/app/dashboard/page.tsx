import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { SignOutButton } from '@/components/SignOutButton'

export default async function Dashboard() {
  const { userId } = await auth()
  
  // This check is redundant with middleware, but good for explicit protection
  if (!userId) {
    redirect('/sign-in')
  }

  const user = await currentUser()

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <SignOutButton />
        </div>

        <div className="bg-white shadow rounded-lg p-6 space-y-4">
          <h2 className="text-xl font-semibold">Welcome back!</h2>
          
          <div className="space-y-2">
            <p><strong>User ID:</strong> {userId}</p>
            <p><strong>Email:</strong> {user?.emailAddresses[0]?.emailAddress}</p>
            <p><strong>Name:</strong> {user?.firstName} {user?.lastName}</p>
          </div>

          <div className="pt-4 border-t">
            <Link
              href="/profile"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              View Full Profile
            </Link>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-2">
            <Link
              href="/dashboard/settings"
              className="block p-3 bg-gray-50 hover:bg-gray-100 rounded transition"
            >
              Settings
            </Link>
            <Link
              href="/api/user"
              className="block p-3 bg-gray-50 hover:bg-gray-100 rounded transition"
            >
              Test Protected API
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

### 8. User Profile Page