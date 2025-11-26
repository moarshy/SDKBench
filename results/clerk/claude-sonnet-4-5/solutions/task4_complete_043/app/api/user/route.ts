import { auth, currentUser } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Get the userId from auth
    const { userId } = auth()

    // Check if user is authenticated
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in' },
        { status: 401 }
      )
    }

    // Get the full user object
    const user = await currentUser()

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // Return user data
    return NextResponse.json({
      success: true,
      data: {
        userId: user.id,
        email: user.emailAddresses?.[0]?.emailAddress || null,
        firstName: user.firstName,
        lastName: user.lastName,
        fullName: `${user.firstName || ''} ${user.lastName || ''}`.trim(),
        imageUrl: user.imageUrl,
        createdAt: user.createdAt,
        lastSignInAt: user.lastSignInAt,
        metadata: {
          publicMetadata: user.publicMetadata,
          privateMetadata: user.privateMetadata,
        },
      },
      message: 'User data retrieved successfully',
    })
  } catch (error) {
    console.error('Error fetching user data:', error)
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

// Optional: Add POST endpoint for updating user metadata
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

    // Here you could update user metadata using Clerk's API
    // For now, just return success
    return NextResponse.json({
      success: true,
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

## Additional Files Needed

You'll also need to create these additional files for a complete integration: