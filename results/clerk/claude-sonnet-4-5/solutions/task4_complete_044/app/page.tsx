import Link from 'next/link'
import { auth } from '@clerk/nextjs/server'
import { UserButton } from '@clerk/nextjs'

export default async function Home() {
  const { userId } = await auth()

  return (
    <div>
      <header className="header">
        <h1>My Secure App</h1>
        <nav className="nav">
          <Link href="/">Home</Link>
          {userId ? (
            <>
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/profile">Profile</Link>
              <UserButton afterSignOutUrl="/" />
            </>
          ) : (
            <>
              <Link href="/sign-in">Sign In</Link>
              <Link href="/sign-up">Sign Up</Link>
            </>
          )}
        </nav>
      </header>

      <div className="container">
        <div className="card">
          <h2>Welcome to Our Application</h2>
          <p style={{ marginTop: '1rem' }}>
            {userId
              ? 'You are signed in! Visit your dashboard to see protected content.'
              : 'Please sign in to access protected features.'}
          </p>
          {!userId && (
            <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
              <Link
                href="/sign-in"
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#0070f3',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '4px',
                }}
              >
                Sign In
              </Link>
              <Link
                href="/sign-up"
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#333',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '4px',
                }}
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

### 6. Sign In Page