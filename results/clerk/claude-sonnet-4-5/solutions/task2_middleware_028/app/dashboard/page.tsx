import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function Dashboard() {
  // Get auth state - this will be populated because middleware protects this route
  const { userId } = auth()
  
  // Double-check authentication (optional, middleware already protects)
  if (!userId) {
    redirect('/sign-in')
  }

  // Get current user details
  const user = await currentUser()

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
        <p className="text-green-800 font-semibold">✓ This route is now protected!</p>
      </div>
      
      <div className="bg-white border rounded-lg p-6 shadow-sm">
        <h2 className="text-xl font-semibold mb-3">User Information</h2>
        <div className="space-y-2">
          <p><strong>User ID:</strong> {userId}</p>
          <p><strong>Email:</strong> {user?.emailAddresses[0]?.emailAddress}</p>
          <p><strong>Name:</strong> {user?.firstName} {user?.lastName}</p>
        </div>
      </div>
    </div>
  )
}

### 3. Update Protected API Route