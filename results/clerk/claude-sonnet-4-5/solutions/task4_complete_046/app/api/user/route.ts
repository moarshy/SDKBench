import { auth, currentUser } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Method 1: Using auth() - gets userId and sessionId
    const { userId } = auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - No user ID found' },
        { status: 401 }
      )
    }

    // Method 2: Using currentUser() - gets full user object
    const user = await currentUser()

    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized - User not found' },
        { status: 401 }
      )
    }

    // Return user data
    return NextResponse.json({
      message: 'User data retrieved successfully',
      user: {
        id: user.id,
        email: user.emailAddresses[0]?.emailAddress,
        firstName: user.firstName,
        lastName: user.lastName,
        imageUrl: user.imageUrl,
        createdAt: user.createdAt,
      },
    })
  } catch (error) {
    console.error('Error in user API route:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const { userId } = auth()

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
    console.error('Error in POST user API route:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

### 11. Public API Route (Example)