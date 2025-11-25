import { auth, clerkClient } from '@clerk/nextjs/server'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const body = await request.json()
    const { firstName, lastName } = body

    // Update user metadata
    await clerkClient.users.updateUser(userId, {
      firstName,
      lastName,
    })

    return NextResponse.json({
      message: 'User updated successfully',
      userId,
    })
  } catch (error) {
    console.error('Error updating user:', error)
    return NextResponse.json(
      { error: 'Failed to update user' },
      { status: 500 }
    )
  }
}

### 14. TypeScript Configuration