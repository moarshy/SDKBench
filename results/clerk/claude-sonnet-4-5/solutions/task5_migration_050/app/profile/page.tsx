import { currentUser } from '@clerk/nextjs/server'

export default async function Profile() {
  const user = await currentUser()

  if (!user) {
    return <div>Not signed in</div>
  }

  return (
    <div>
      <h1>{user.firstName}</h1>
      <p>{user.emailAddresses[0]?.emailAddress}</p>
    </div>
  )
}

### 2. Update Middleware (if you have one)