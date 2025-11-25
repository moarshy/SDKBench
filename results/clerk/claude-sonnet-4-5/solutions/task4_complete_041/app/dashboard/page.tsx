import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import { UserButton } from '@clerk/nextjs'
import Link from 'next/link'

export default async function Dashboard() {
  // Get authentication state
  const { userId } = await auth()
  
  // Redirect if not authenticated (backup check)
  if (!userId) {
    redirect('/sign-in')
  }

  // Get full user object
  const user = await currentUser()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <div className="flex items-center gap-4">
            <Link 
              href="/profile" 
              className="text-blue-600 hover:text-blue-800"
            >
              Profile
            </Link>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">
            Welcome, {user?.firstName || 'User'}!
          </h2>
          
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="font-medium">{user?.emailAddresses[0]?.emailAddress}</p>
            </div>
            
            <div>
              <p className="text-sm text-gray-600">User ID</p>
              <p className="font-mono text-sm">{userId}</p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Account Created</p>
              <p className="font-medium">
                {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* Additional Dashboard Content */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <DashboardCard 
            title="Profile" 
            description="Manage your account settings"
            href="/profile"
          />
          <DashboardCard 
            title="Settings" 
            description="Configure your preferences"
            href="/settings"
          />
          <DashboardCard 
            title="API Access" 
            description="View your API credentials"
            href="/api-keys"
          />
        </div>
      </main>
    </div>
  )
}

function DashboardCard({ 
  title, 
  description, 
  href 
}: { 
  title: string
  description: string
  href: string 
}) {
  return (
    <Link 
      href={href}
      className="block bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
    >
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </Link>
  )
}

### 8. User Profile Page