import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { UserButton } from '@clerk/nextjs'

export default async function Dashboard() {
  // Get authentication state
  const { userId } = await auth()
  
  // Redirect if not authenticated (extra safety, middleware handles this too)
  if (!userId) {
    redirect('/sign-in')
  }

  // Get full user object
  const user = await currentUser()

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header with User Button */}
        <header className="flex justify-between items-center mb-8 pb-4 border-b">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">
              {user?.emailAddresses[0]?.emailAddress}
            </span>
            <UserButton afterSignOutUrl="/" />
          </div>
        </header>

        {/* User Information */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">User Information</h2>
            <div className="space-y-2">
              <p><strong>Name:</strong> {user?.firstName} {user?.lastName}</p>
              <p><strong>Email:</strong> {user?.emailAddresses[0]?.emailAddress}</p>
              <p><strong>User ID:</strong> {userId}</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <Link 
                href="/dashboard/profile" 
                className="block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-center"
              >
                View Profile
              </Link>
              <Link 
                href="/dashboard/settings" 
                className="block px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-center"
              >
                Settings
              </Link>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Account Status</h2>
            <div className="space-y-2">
              <p><strong>Status:</strong> <span className="text-green-600">Active</span></p>
              <p><strong>Created:</strong> {new Date(user?.createdAt || '').toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

### 8. User Profile Page