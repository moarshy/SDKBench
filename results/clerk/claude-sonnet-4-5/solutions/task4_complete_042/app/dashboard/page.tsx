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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow p-6">
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

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-semibold text-gray-700 mb-2">User ID</h3>
                <p className="text-sm text-gray-600 font-mono break-all">
                  {userId}
                </p>
              </div>

              {user?.emailAddresses?.[0]?.emailAddress && (
                <div className="bg-gray-50 p-4 rounded">
                  <h3 className="font-semibold text-gray-700 mb-2">Email</h3>
                  <p className="text-sm text-gray-600">
                    {user.emailAddresses[0].emailAddress}
                  </p>
                </div>
              )}

              {user?.firstName && (
                <div className="bg-gray-50 p-4 rounded">
                  <h3 className="font-semibold text-gray-700 mb-2">
                    First Name
                  </h3>
                  <p className="text-sm text-gray-600">{user.firstName}</p>
                </div>
              )}

              {user?.lastName && (
                <div className="bg-gray-50 p-4 rounded">
                  <h3 className="font-semibold text-gray-700 mb-2">
                    Last Name
                  </h3>
                  <p className="text-sm text-gray-600">{user.lastName}</p>
                </div>
              )}
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded">
              <h3 className="font-semibold text-blue-900 mb-2">
                Protected Content
              </h3>
              <p className="text-sm text-blue-800">
                This page is protected by Clerk middleware. Only authenticated
                users can access this content.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}