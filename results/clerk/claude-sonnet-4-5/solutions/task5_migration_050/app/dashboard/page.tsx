import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function Dashboard() {
  const { userId } = auth()

  if (!userId) {
    redirect('/sign-in')
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <p>User ID: {userId}</p>
    </div>
  )
}

### Example: Using currentUser() with Full User Data