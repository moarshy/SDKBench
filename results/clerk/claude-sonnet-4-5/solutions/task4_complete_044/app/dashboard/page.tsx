import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { SignOutButton } from '@clerk/nextjs'

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
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <SignOutButton>
              <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                Sign Out
              </button>
            </SignOutButton>
          </div>

          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Welcome back!
            </h2>
            
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-sm font-medium text-gray-500">User ID</p>
                <p className="mt-1 text-sm text-gray-900">{userId}</p>
              </div>

              {user?.emailAddresses && user.emailAddresses.length > 0 && (
                <div className="bg-gray-50 p-4 rounded-md">
                  <p className="text-sm font-medium text-gray-500">Email</p>
                  <p className="mt-1 text-sm text-gray-900">
                    {user.emailAddresses[0].emailAddress}
                  </p>
                </div>
              )}

              {user?.firstName && (
                <div className="bg-gray-50 p-4 rounded-md">
                  <p className="text-sm font-medium text-gray-500">Name</p>
                  <p className="mt-1 text-sm text-gray-900">
                    {user.firstName} {user.lastName || ''}
                  </p>
                </div>
              )}

              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-sm font-medium text-gray-500">
                  Account Created
                </p>
                <p className="mt-1 text-sm text-gray-900">
                  {user?.createdAt 
                    ? new Date(user.createdAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })
                    : 'N/A'}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-3">
              Quick Actions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <a
                href="/user-profile"
                className="block p-4 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
              >
                <p className="font-medium text-blue-900">Edit Profile</p>
                <p className="text-sm text-blue-700 mt-1">
                  Update your account information
                </p>
              </a>
              <a
                href="/api/user"
                className="block p-4 bg-green-50 hover:bg-green-100 rounded-md transition-colors"
              >
                <p className="font-medium text-green-900">API Test</p>
                <p className="text-sm text-green-700 mt-1">
                  Test protected API endpoint
                </p>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}