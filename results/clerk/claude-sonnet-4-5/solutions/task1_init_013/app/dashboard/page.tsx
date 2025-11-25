import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  // Get auth state
  const { userId } = auth()
  
  // Redirect if not authenticated (backup to middleware)
  if (!userId) {
    redirect('/sign-in')
  }

  // Get full user object
  const user = await currentUser()

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Protected Dashboard</h1>
      <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
        <h2>User Information</h2>
        <p><strong>User ID:</strong> {userId}</p>
        {user && (
          <>
            <p><strong>Email:</strong> {user.emailAddresses[0]?.emailAddress}</p>
            <p><strong>Name:</strong> {user.firstName} {user.lastName}</p>
            <p><strong>Created:</strong> {new Date(user.createdAt).toLocaleDateString()}</p>
          </>
        )}
      </div>
    </div>
  )
}

## Step 9: Add Global Styles (Optional)