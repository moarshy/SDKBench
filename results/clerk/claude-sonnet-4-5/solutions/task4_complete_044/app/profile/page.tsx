import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { UserButton, UserProfile } from '@clerk/nextjs'

export default async function ProfilePage() {
  const { userId } = await auth()
  
  if (!userId) {
    redirect('/sign-in')
  }

  return (
    <div>
      <header className="header">
        <h1>Profile</h1>
        <nav className="nav">
          <Link href="/">Home</Link>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/profile">Profile</Link>
          <UserButton afterSignOutUrl="/" />
        </nav>
      </header>

      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <UserProfile />
        </div>
      </div>
    </div>
  )
}

### 10. Protected API Route