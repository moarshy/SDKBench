import { currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const user = await currentUser()

  if (!user) {
    redirect('/sign-in')
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Dashboard</h1>
      <p>Welcome to your protected dashboard, {user.firstName}!</p>
      <div style={{ marginTop: '1rem' }}>
        <h2>User Information:</h2>
        <ul>
          <li>ID: {user.id}</li>
          <li>Email: {user.emailAddresses[0].emailAddress}</li>
          <li>
            Name: {user.firstName} {user.lastName}
          </li>
        </ul>
      </div>
    </div>
  )
}

## Installation & Setup Instructions

1. **Install dependencies:**