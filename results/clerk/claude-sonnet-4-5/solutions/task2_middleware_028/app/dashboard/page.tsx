import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function Dashboard() {
  // Get the auth state
  const { userId } = await auth()
  
  // If no user is signed in, redirect to sign-in page
  if (!userId) {
    redirect('/sign-in')
  }
  
  // Get the current user's details
  const user = await currentUser()

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <p className="mb-4">
        Welcome, {user?.firstName || user?.emailAddresses[0]?.emailAddress}!
      </p>
      <p className="text-green-600 font-semibold">
        ✓ This route is now protected by Clerk authentication
      </p>
      <div className="mt-6 p-4 bg-gray-100 rounded">
        <h2 className="font-semibold mb-2">User Information:</h2>
        <ul className="space-y-1">
          <li>User ID: {userId}</li>
          <li>Email: {user?.emailAddresses[0]?.emailAddress}</li>
          <li>Name: {user?.firstName} {user?.lastName}</li>
        </ul>
      </div>
    </div>
  )
}