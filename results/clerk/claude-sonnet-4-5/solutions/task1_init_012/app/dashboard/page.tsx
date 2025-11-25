import { currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const user = await currentUser()

  if (!user) {
    redirect('/sign-in')
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Protected Dashboard</h1>
      <p>Welcome, {user.firstName}! This page is only accessible to authenticated users.</p>
      <div style={{ marginTop: '2rem' }}>
        <h2>Your Profile:</h2>
        <pre style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '8px', overflow: 'auto' }}>
          {JSON.stringify(
            {
              id: user.id,
              email: user.emailAddresses[0].emailAddress,
              firstName: user.firstName,
              lastName: user.lastName,
            },
            null,
            2
          )}
        </pre>
      </div>
    </div>
  )
}

## Step 9: Create Custom Sign-In Page (Optional)