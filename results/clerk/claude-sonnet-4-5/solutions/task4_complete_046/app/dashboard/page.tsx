import { currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { UserButton } from '@clerk/nextjs'

export default async function Dashboard() {
  const user = await currentUser()

  if (!user) {
    redirect('/sign-in')
  }

  return (
    <>
      <header className="header">
        <nav className="nav">
          <div>
            <Link href="/" style={{ fontSize: '1.5rem', fontWeight: 'bold', textDecoration: 'none', color: '#6366f1' }}>
              MyApp
            </Link>
          </div>
          <div className="nav-links">
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/profile">Profile</Link>
            <UserButton afterSignOutUrl="/" />
          </div>
        </nav>
      </header>

      <main className="container">
        <div className="card">
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>
            Welcome back, {user.firstName || 'User'}! 👋
          </h1>
          <p style={{ color: '#666', marginBottom: '2rem' }}>
            This is your protected dashboard
          </p>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '1.5rem',
            marginTop: '2rem'
          }}>
            <div style={{ 
              padding: '1.5rem', 
              background: '#f0f9ff', 
              borderRadius: '8px',
              border: '1px solid #bae6fd'
            }}>
              <h3 style={{ marginBottom: '0.5rem' }}>📧 Email</h3>
              <p style={{ color: '#666' }}>
                {user.emailAddresses[0]?.emailAddress || 'No email'}
              </p>
            </div>

            <div style={{ 
              padding: '1.5rem', 
              background: '#f0fdf4', 
              borderRadius: '8px',
              border: '1px solid #bbf7d0'
            }}>
              <h3 style={{ marginBottom: '0.5rem' }}>🆔 User ID</h3>
              <p style={{ color: '#666', fontSize: '0.875rem', wordBreak: 'break-all' }}>
                {user.id}
              </p>
            </div>

            <div style={{ 
              padding: '1.5rem', 
              background: '#fef3c7', 
              borderRadius: '8px',
              border: '1px solid #fde68a'
            }}>
              <h3 style={{ marginBottom: '0.5rem' }}>📅 Member Since</h3>
              <p style={{ color: '#666' }}>
                {new Date(user.createdAt).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 style={{ marginBottom: '1rem' }}>Quick Actions</h2>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <Link href="/profile">
              <button className="button">View Profile</button>
            </Link>
            <Link href="/api/user">
              <button className="button" style={{ background: '#10b981' }}>
                Test API
              </button>
            </Link>
          </div>
        </div>
      </main>
    </>
  )
}

### 9. User Profile Page