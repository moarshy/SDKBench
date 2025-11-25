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
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <SignOutButton>
              <button className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
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

            <div className="bg-gray-50 rounded-md p-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                User Information
              </h3>
              <div className="space-y-2">
                <div className="flex items-center">
                  <span className="font-medium text-gray-700 w-32">User ID:</span>
                  <span className="text-gray-600">{userId}</span>
                </div>
                {user?.emailAddresses?.[0]?.emailAddress && (
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-32">Email:</span>
                    <span className="text-gray-600">
                      {user.emailAddresses[0].emailAddress}
                    </span>
                  </div>
                )}
                {user?.firstName && (
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-32">First Name:</span>
                    <span className="text-gray-600">{user.firstName}</span>
                  </div>
                )}
                {user?.lastName && (
                  <div className="flex items-center">
                    <span className="font-medium text-gray-700 w-32">Last Name:</span>
                    <span className="text-gray-600">{user.lastName}</span>
                  </div>
                )}
                <div className="flex items-center">
                  <span className="font-medium text-gray-700 w-32">Created:</span>
                  <span className="text-gray-600">
                    {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                Protected Content
              </h3>
              <p className="text-blue-800">
                This page is protected by Clerk middleware. Only authenticated users can access this content.
              </p>
            </div>

            <div className="mt-6">
              <a
                href="/api/user"
                className="inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Test Protected API Route
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}