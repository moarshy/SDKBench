import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function Dashboard() {
  // Server-side authentication check
  const { userId } = await auth()
  
  // This is redundant with middleware, but good for defense in depth
  if (!userId) {
    redirect('/sign-in')
  }

  // Get full user details if needed
  const user = await currentUser()

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <p className="mb-4">Welcome, {user?.firstName || 'User'}!</p>
      <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
        <p className="font-bold">✓ This page is now protected!</p>
        <p className="text-sm mt-2">User ID: {userId}</p>
        <p className="text-sm">Email: {user?.emailAddresses[0]?.emailAddress}</p>
      </div>
    </div>
  )
}