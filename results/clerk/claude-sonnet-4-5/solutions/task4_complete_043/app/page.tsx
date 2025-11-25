import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton } from '@clerk/nextjs'
import Link from 'next/link'

export default async function Home() {
  const { userId } = await auth()

  return (
    <div>
      <nav className="nav">
        <div>
          <Link href="/">
            <h1 style={{ margin: 0 }}>My App</h1>
          </Link>
        </div>
        <div className="nav-links">
          {userId ? (
            <>
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/profile">Profile</Link>
            </>
          ) : (
            <>
              <SignInButton mode="modal">
                <button className="btn btn-primary">Sign In</button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="btn">Sign Up</button>
              </SignUpButton>
            </>
          )}
        </div>
      </nav>

      <div className="container">
        <div className="card">
          <h1>Welcome to My App</h1>
          <p>
            {userId
              ? 'You are signed in! Check out your dashboard.'
              : 'Please sign in to access your dashboard.'}
          </p>
          {userId && (
            <Link href="/dashboard">
              <button className="btn btn-primary" style={{ marginTop: '1rem' }}>
                Go to Dashboard
              </button>
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}

### 6. Sign In Page