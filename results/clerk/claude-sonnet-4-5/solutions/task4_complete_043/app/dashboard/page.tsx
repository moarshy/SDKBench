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
              <button className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition">
                Sign Out
              </button>
            </SignOutButton>
          </div>

          <div className="space-y-4">
            <div className="border-b pb-4">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                Welcome back!
              </h2>
              <p className="text-gray-600">
                You are successfully authenticated with Clerk.
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-800">
                User Information
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-500">User ID</p>
                  <p className="font-medium text-gray-900">{userId}</p>
                </div>

                {user?.emailAddresses?.[0]?.emailAddress && (
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-500">Email</p>
                    <p className="font-medium text-gray-900">
                      {user.emailAddresses[0].emailAddress}
                    </p>
                  </div>
                )}

                {user?.firstName && (
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-500">First Name</p>
                    <p className="font-medium text-gray-900">
                      {user.firstName}
                    </p>
                  </div>
                )}

                {user?.lastName && (
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-500">Last Name</p>
                    <p className="font-medium text-gray-900">
                      {user.lastName}
                    </p>
                  </div>
                )}

                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-500">Created At</p>
                  <p className="font-medium text-gray-900">
                    {user?.createdAt 
                      ? new Date(user.createdAt).toLocaleDateString()
                      : 'N/A'}
                  </p>
                </div>

                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-500">Last Sign In</p>
                  <p className="font-medium text-gray-900">
                    {user?.lastSignInAt 
                      ? new Date(user.lastSignInAt).toLocaleDateString()
                      : 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Protected Features
              </h3>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li>This page is protected by Clerk middleware</li>
                <li>Only authenticated users can access this content</li>
                <li>User session is managed automatically</li>
                <li>API routes are also protected</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}