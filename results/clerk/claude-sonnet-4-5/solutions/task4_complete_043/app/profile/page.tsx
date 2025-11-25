import { UserProfile } from '@clerk/nextjs'
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'

export default async function ProfilePage() {
  const { userId } = await auth()
  
  if (!userId) {
    redirect('/sign-in')
  }

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
        </div>
      </nav>

      <div className="container">
        <h1 style={{ marginBottom: '2rem' }}>User Profile</h1>
        <UserProfile 
          appearance={{
            elements: {
              rootBox: 'w-full',
              card: 'shadow-lg'
            }
          }}
        />
      </div>
    </div>
  )
}

### 10. Protected API Route