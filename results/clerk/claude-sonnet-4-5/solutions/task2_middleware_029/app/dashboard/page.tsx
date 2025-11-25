import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function Dashboard() {
  // Get auth state
  const { userId } = auth()
  
  // This is redundant with middleware but provides defense in depth
  if (!userId) {
    redirect('/sign-in')
  }

  // Get full user object if needed
  const user = await currentUser()

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <p className="mb-4">This page is now protected by Clerk authentication.</p>
      
      <div className="bg-gray-100 p-4 rounded-lg">
        <h2 className="text-xl font-semibold mb-2">User Information</h2>
        <p><strong>User ID:</strong> {userId}</p>
        {user && (
          <>
            <p><strong>Email:</strong> {user.emailAddresses[0]?.emailAddress}</p>
            <p><strong>Name:</strong> {user.firstName} {user.lastName}</p>
          </>
        )}
      </div>
    </div>
  )
}

### 3. Update Protected API Route