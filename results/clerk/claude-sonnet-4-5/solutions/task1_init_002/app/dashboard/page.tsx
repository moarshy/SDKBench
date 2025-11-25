import { currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const user = await currentUser()

  if (!user) {
    redirect('/sign-in')
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Protected Dashboard</h1>
      <p>This page is only accessible to authenticated users.</p>
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
        <h2>Welcome, {user.firstName}!</h2>
        <p>Your user ID: {user.id}</p>
      </div>
    </div>
  )
}

## Setup Instructions

1. **Install dependencies:**