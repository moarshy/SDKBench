import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import SettingsClient from './settings-client'

export default async function SettingsPage() {
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
        
        <h1 className="text-3xl font-bold mb-8">Settings</h1>
        
        <SettingsClient />
      </div>
    </div>
  )
}