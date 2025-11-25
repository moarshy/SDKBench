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
      <nav className="bg-white shadow-sm">
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
            <div>
              <h3 className="text-sm font-medium text-gray-500">Email</h3>
              <p className="mt-1 text-sm text-gray-900">
                {user?.emailAddresses[0]?.emailAddress}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500">User ID</h3>
              <p className="mt-1 text-sm text-gray-900 font-mono">
                {userId}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500">Account Created</h3>
              <p className="mt-1 text-sm text-gray-900">
                {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
              </p>
            </div>

            <div className="pt-4 border-t">
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Profile Information
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500">First Name</p>
                  <p className="text-sm font-medium">
                    {user?.firstName || 'Not set'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Last Name</p>
                  <p className="text-sm font-medium">
                    {user?.lastName || 'Not set'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-900 mb-2">
            🎉 Authentication Complete!
          </h3>
          <p className="text-sm text-blue-700">
            Your application is now protected with Clerk authentication. 
            This dashboard is only accessible to authenticated users.
          </p>
        </div>
      </main>
    </div>
  )
}