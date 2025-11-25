import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function POST(req: NextRequest) {
  // Auth check - no longer needs req parameter
  const { userId } = await auth()

  if (!userId) {
    return new Response('Unauthorized', { status: 401 })
  }

  // You can still use req for body parsing
  const body = await req.json()

  return NextResponse.json({ 
    userId, 
    message: 'Created successfully',
    data: body 
  })
}

### Example 2: Multiple Auth Properties