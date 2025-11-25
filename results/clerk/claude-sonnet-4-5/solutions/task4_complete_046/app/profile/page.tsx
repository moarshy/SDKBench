import { UserProfile } from '@clerk/nextjs'
import Link from 'next/link'
import { UserButton } from '@clerk/nextjs'

export default function ProfilePage() {
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
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          padding: '2rem 0'
        }}>
          <UserProfile 
            appearance={{
              elements: {
                rootBox: 'w-full',
                card: 'shadow-lg'
              }
            }}
          />
        </div>
      </main>
    </>
  )
}

### 10. Protected API Route