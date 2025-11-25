import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  // Get auth state
  const { userId } = auth()
  
  // Redirect if not authenticated (backup protection)
  if (!userId) {
    redirect('/sign-in')
  }

  // Get full user object
  const user = await currentUser()

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Dashboard</h1>
      <p>Welcome, {user?.firstName || 'User'}!</p>
      <div style={{ marginTop: '2rem' }}>
        <h2>User Information:</h2>
        <ul style={{ marginTop: '1rem', lineHeight: '1.8' }}>
          <li><strong>User ID:</strong> {userId}</li>
          <li><strong>Email:</strong> {user?.emailAddresses[0]?.emailAddress}</li>
          <li><strong>Name:</strong> {user?.firstName} {user?.lastName}</li>
        </ul>
      </div>
    </div>
  )
}

## Step 9: Create Type Definitions (Optional but Recommended)