import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  // Get the authentication state
  const { userId } = auth()

  // Check if user is authenticated
  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  // Return protected data
  return NextResponse.json({ 
    message: 'This is protected data',
    userId: userId 
  })
}