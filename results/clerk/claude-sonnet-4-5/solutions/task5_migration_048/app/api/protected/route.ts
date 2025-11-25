import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized', code: 'NO_AUTH' },
        { status: 401 }
      )
    }

    // Your protected logic here
    const data = await fetchProtectedData(userId)

    return NextResponse.json({ success: true, data })
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { error: 'Internal Server Error', code: 'SERVER_ERROR' },
      { status: 500 }
    )
  }
}

async function fetchProtectedData(userId: string) {
  // Your data fetching logic
  return { userId, message: 'Protected data' }
}

### Example 5: Dynamic Route with Auth