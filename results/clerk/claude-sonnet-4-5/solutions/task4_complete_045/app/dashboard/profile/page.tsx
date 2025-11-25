import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { UserProfile } from '@clerk/nextjs'
import Link from 'next/link'

export default async function ProfilePage() {
  const { userId } = await auth()
  
  if (!userId) {
    redirect('/sign-in')
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Link 
            href="/dashboard" 
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to Dashboard
          </Link>
        </div>
        
        <h1 className="text-3xl font-bold mb-8">User Profile</h1>
        
        <UserProfile 
          appearance={{
            elements: {
              rootBox: "w-full",
              card: "shadow-xl"
            }
          }}
        />
      </div>
    </div>
  )
}

### 9. Settings Page with Client Component