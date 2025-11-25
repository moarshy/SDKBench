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
      createdAt: user?.createdAt,
    })
  } catch (error) {
    console.error('Error in user API:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const body = await request.json()

    // Process the request with authenticated user
    return NextResponse.json({
      message: 'Data processed successfully',
      userId,
      data: body,
    })
  } catch (error) {
    console.error('Error in user API POST:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

### 11. Public API Route Example