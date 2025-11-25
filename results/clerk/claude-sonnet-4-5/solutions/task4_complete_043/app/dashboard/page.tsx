import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { SignOutButton } from '@clerk/nextjs'

export default async function Dashboard() {
  const { userId } = await auth()
  
  // Double-check authentication (middleware should handle this, but good practice)
  if (!userId) {
    redirect('/sign-in')
  }

  const user = await currentUser()

  return (
    <div>
      <nav className="nav">
        <div>
          <Link href="/">
            <h1 style={{ margin: 0 }}>My App</h1>
          </Link>
        </div>
        <div className="nav-links">
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/profile">Profile</Link>
          <SignOutButton>
            <button className="btn">Sign Out</button>
          </SignOutButton>
        </div>
      </nav>

      <div className="container">
        <div className="card">
          <h1>Dashboard</h1>
          <p>Welcome back, {user?.firstName || 'User'}!</p>
          
          <div style={{ marginTop: '2rem' }}>
            <h2>Your Information</h2>
            <ul style={{ marginTop: '1rem', listStyle: 'none' }}>
              <li><strong>User ID:</strong> {userId}</li>
              <li><strong>Email:</strong> {user?.emailAddresses[0]?.emailAddress}</li>
              <li><strong>Name:</strong> {user?.firstName} {user?.lastName}</li>
              <li><strong>Username:</strong> {user?.username || 'Not set'}</li>
            </ul>
          </div>

          <div style={{ marginTop: '2rem' }}>
            <h2>Quick Actions</h2>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              <Link href="/profile">
                <button className="btn btn-primary">Edit Profile</button>
              </Link>
              <Link href="/api/user">
                <button className="btn">Test API</button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

### 9. User Profile Page