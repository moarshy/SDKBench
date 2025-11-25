import { currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function Settings() {
  const user = await currentUser()

  if (!user) {
    redirect('/sign-in')
  }

  return (
    <div>
      <h1>Settings</h1>
      <div>
        <p>Name: {user.firstName} {user.lastName}</p>
        <p>Email: {user.emailAddresses[0]?.emailAddress}</p>
        <p>Username: {user.username}</p>
        <img src={user.imageUrl} alt="Profile" />
      </div>
    </div>
  )
}

### Example: API Route with Clerk v5