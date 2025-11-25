import { auth, currentUser } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Get authentication state
    const { userId } = auth()

    // Return 401 if not authenticated
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in' },
        { status: 401 }
      )
    }

    // Get current user details
    const user = await currentUser()

    // Return user data
    return NextResponse.json({
      message: 'User data retrieved successfully',
      user: {
        id: userId,
        email: user?.emailAddresses?.[0]?.emailAddress,
        firstName: user?.firstName,
        lastName: user?.lastName,
        fullName: user?.firstName && user?.lastName 
          ? `${user.firstName} ${user.lastName}` 
          : null,
        imageUrl: user?.imageUrl,
        createdAt: user?.createdAt,
        lastSignInAt: user?.lastSignInAt,
      },
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Error fetching user data:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

## Additional Required Files

You'll also need to create these sign-in and sign-up pages: