import { auth, currentUser } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const { userId } = auth()

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const user = await currentUser()

  return NextResponse.json({
    userId,
    email: user?.emailAddresses[0]?.emailAddress,
    firstName: user?.firstName,
  })
}

### Example: Server Action with Clerk v5