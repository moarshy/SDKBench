import { auth, currentUser } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Get authentication state
    const { userId } = await auth()

    // Return 401 if not authenticated
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // Get full user data
    const user = await currentUser()

    // Return user data
    return NextResponse.json({
      userId,
      email: user?.emailAddresses[0]?.emailAddress,
      firstName: user?.firstName,
      lastName: user?.lastName,
      imageUrl: user?.imageUrl,
      createdAt: user?.createdAt,
    })
  } catch (error) {
    console.error('Error fetching user:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function PATCH(request: Request) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const body = await request.json()
    
    // Here you would update user data in your database
    // This is just an example response
    return NextResponse.json({
      success: true,
      message: 'User updated successfully',
      data: body,
    })
  } catch (error) {
    console.error('Error updating user:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

### 10. Public API Route Example