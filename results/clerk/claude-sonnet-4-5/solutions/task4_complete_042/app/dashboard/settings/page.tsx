import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { UserInfo } from '@/components/UserInfo'

export default async function SettingsPage() {
  const { userId } = await auth()
  
  if (!userId) {
    redirect('/sign-in')
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Link
            href="/dashboard"
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to Dashboard
          </Link>
        </div>

        <h1 className="text-3xl font-bold">Settings</h1>

        <div className="bg-white shadow rounded-lg p-6 space-y-4">
          <h2 className="text-xl font-semibold">Account Information</h2>
          <UserInfo />
          
          <div className="pt-4 border-t">
            <Link
              href="/profile"
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition inline-block"
            >
              Edit Profile
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

### 14. Global CSS (Optional Styling)