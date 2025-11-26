import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { UserButton } from '@clerk/nextjs'

export default async function Dashboard() {
  // Get authentication state
  const { userId } = auth()
  
  // Redirect to sign-in if not authenticated
  if (!userId) {
    redirect('/sign-in')
  }

  // Get current user details
  const user = await currentUser()

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-semibold">Dashboard</h1>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-4">
            Welcome, {user?.firstName || 'User'}!
          </h2>
          
          <div className="space-y-4">
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold mb-2">Profile Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-medium">
                    {user?.emailAddresses[0]?.emailAddress}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">User ID</p>
                  <p className="font-medium font-mono text-sm">{userId}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Full Name</p>
                  <p className="font-medium">
                    {user?.firstName} {user?.lastName}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Account Created</p>
                  <p className="font-medium">
                    {user?.createdAt
                      ? new Date(user.createdAt).toLocaleDateString()
                      : 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Quick Actions</h3>
              <div className="flex gap-4">
                <button className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition">
                  Edit Profile
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition">
                  Settings
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}