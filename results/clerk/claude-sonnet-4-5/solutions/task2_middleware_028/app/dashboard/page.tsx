import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function Dashboard() {
  // Get the auth state
  const { userId } = await auth()
  
  // If no userId, redirect to sign-in (this is a backup, middleware should handle this)
  if (!userId) {
    redirect('/sign-in')
  }

  // Get the current user details
  const user = await currentUser()

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-lg mb-4">
          Welcome, {user?.firstName || user?.emailAddresses[0]?.emailAddress || 'User'}!
        </p>
        <p className="text-gray-600">
          This page is now protected by Clerk authentication middleware.
        </p>
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <p className="text-sm font-semibold mb-2">User Info:</p>
          <ul className="text-sm space-y-1">
            <li><strong>User ID:</strong> {userId}</li>
            <li><strong>Email:</strong> {user?.emailAddresses[0]?.emailAddress}</li>
            <li><strong>Name:</strong> {user?.firstName} {user?.lastName}</li>
          </ul>
        </div>
      </div>
    </div>
  )
}