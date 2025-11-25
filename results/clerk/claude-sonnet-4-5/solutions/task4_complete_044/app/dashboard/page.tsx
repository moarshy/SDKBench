import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { UserButton } from '@clerk/nextjs'

export default async function Dashboard() {
  // Get authentication state
  const { userId } = await auth()
  
  // Redirect if not authenticated (extra safety, middleware also protects)
  if (!userId) {
    redirect('/sign-in')
  }

  // Get full user object
  const user = await currentUser()

  return (
    <div>
      <header className="header">
        <h1>Dashboard</h1>
        <nav className="nav">
          <Link href="/">Home</Link>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/profile">Profile</Link>
          <UserButton afterSignOutUrl="/" />
        </nav>
      </header>

      <div className="container">
        <div className="card">
          <h2>Welcome to Your Dashboard</h2>
          <p style={{ marginTop: '1rem' }}>
            Hello, {user?.firstName || user?.emailAddresses[0]?.emailAddress}!
          </p>
          
          <div style={{ marginTop: '2rem' }}>
            <h3>User Information:</h3>
            <ul style={{ marginTop: '1rem', lineHeight: '1.8' }}>
              <li><strong>User ID:</strong> {userId}</li>
              <li><strong>Email:</strong> {user?.emailAddresses[0]?.emailAddress}</li>
              <li><strong>Name:</strong> {user?.firstName} {user?.lastName}</li>
              <li>
                <strong>Created:</strong>{' '}
                {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
              </li>
            </ul>
          </div>

          <div style={{ marginTop: '2rem' }}>
            <h3>Protected Features:</h3>
            <p style={{ marginTop: '0.5rem' }}>
              This page is only accessible to authenticated users.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

### 9. User Profile Page