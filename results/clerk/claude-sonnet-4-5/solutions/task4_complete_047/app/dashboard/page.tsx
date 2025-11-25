import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { UserButton } from '@clerk/nextjs'
import Link from 'next/link'

export default async function Dashboard() {
  // Get authentication state
  const { userId } = await auth()
  
  // Redirect to sign-in if not authenticated
  if (!userId) {
    redirect('/sign-in')
  }

  // Get full user object
  const user = await currentUser()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <div className="flex items-center gap-4">
              <Link 
                href="/profile" 
                className="text-blue-600 hover:text-blue-800"
              >
                Profile
              </Link>
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">
            Welcome, {user?.firstName || 'User'}!
          </h2>
          
          <div className="space-y-4">
            <div className="border-b pb-4">
              <h3 className="font-medium text-gray-700">Account Information</h3>
              <dl className="mt-2 space-y-2">
                <div>
                  <dt className="text-sm text-gray-500">Email</dt>
                  <dd className="text-sm font-medium">
                    {user?.emailAddresses[0]?.emailAddress}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">User ID</dt>
                  <dd className="text-sm font-medium font-mono">{userId}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Member Since</dt>
                  <dd className="text-sm font-medium">
                    {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                  </dd>
                </div>
              </dl>
            </div>

            <div>
              <h3 className="font-medium text-gray-700 mb-2">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Link
                  href="/profile"
                  className="p-4 border rounded-lg hover:bg-gray-50 transition"
                >
                  <h4 className="font-medium">Edit Profile</h4>
                  <p className="text-sm text-gray-600">
                    Update your account settings
                  </p>
                </Link>
                <Link
                  href="/api/user"
                  className="p-4 border rounded-lg hover:bg-gray-50 transition"
                >
                  <h4 className="font-medium">API Test</h4>
                  <p className="text-sm text-gray-600">
                    Test protected API route
                  </p>
                </Link>
                <div className="p-4 border rounded-lg bg-gray-50">
                  <h4 className="font-medium">Settings</h4>
                  <p className="text-sm text-gray-600">
                    Coming soon...
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

### 8. User Profile Page