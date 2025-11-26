import { auth, currentUser } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Get the authentication state
    const { userId } = auth()

    // Check if user is authenticated
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in' },
        { status: 401 }
      )
    }

    // Get the current user's details
    const user = await currentUser()

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
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
        fullName: `${user.firstName} ${user.lastName}`,
        imageUrl: user.imageUrl,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt,
        metadata: {
          publicMetadata: user.publicMetadata,
          privateMetadata: user.privateMetadata,
        },
      },
    })
  } catch (error) {
    console.error('Error fetching user data:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// POST endpoint for updating user data
export async function POST(request: Request) {
  try {
    const { userId } = auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in' },
        { status: 401 }
      )
    }

    const body = await request.json()

    // Here you would typically update user data
    // For example, using Clerk's user update API or your database

    return NextResponse.json({
      message: 'User data updated successfully',
      data: body,
    })
  } catch (error) {
    console.error('Error updating user data:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

## Additional Required Files

You'll also need to create these sign-in and sign-up pages: