import { auth, currentUser } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Option 1: Just get userId
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized' }, 
      { status: 401 }
    )
  }

  // Option 2: Get full user object
  const user = await currentUser()

  if (!user) {
    return NextResponse.json(
      { error: 'User not found' }, 
      { status: 404 }
    )
  }

  return NextResponse.json({ 
    id: user.id,
    email: user.emailAddresses[0]?.emailAddress,
    firstName: user.firstName,
    lastName: user.lastName,
    imageUrl: user.imageUrl
  })
}

### Example 4: Error Handling Pattern