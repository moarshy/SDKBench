import Link from 'next/link'
import { SignedIn, SignedOut, UserButton } from '@clerk/nextjs'

export default function Home() {
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
            <SignedIn>
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/profile">Profile</Link>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
            <SignedOut>
              <Link href="/sign-in">Sign In</Link>
              <Link href="/sign-up">Sign Up</Link>
            </SignedOut>
          </div>
        </nav>
      </header>

      <main className="container">
        <div className="card">
          <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
            Welcome to MyApp
          </h1>
          <p style={{ fontSize: '1.2rem', color: '#666', marginBottom: '2rem' }}>
            A secure application powered by Clerk authentication
          </p>
          
          <SignedOut>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <Link href="/sign-up">
                <button className="button">Get Started</button>
              </Link>
              <Link href="/sign-in">
                <button className="button" style={{ background: 'white', color: '#6366f1', border: '2px solid #6366f1' }}>
                  Sign In
                </button>
              </Link>
            </div>
          </SignedOut>

          <SignedIn>
            <Link href="/dashboard">
              <button className="button">Go to Dashboard</button>
            </Link>
          </SignedIn>
        </div>

        <div className="card">
          <h2 style={{ marginBottom: '1rem' }}>Features</h2>
          <ul style={{ lineHeight: '2', paddingLeft: '1.5rem' }}>
            <li>🔐 Secure authentication with Clerk</li>
            <li>👤 User profile management</li>
            <li>🛡️ Protected routes and API endpoints</li>
            <li>📱 Responsive design</li>
            <li>⚡ Built with Next.js 14</li>
          </ul>
        </div>
      </main>
    </>
  )
}

### 6. Sign In Page