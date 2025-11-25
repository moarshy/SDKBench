import { getAuth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function GET(req: NextRequest) {
  const { userId } = getAuth(req)

  if (!userId) {
    return new Response('Unauthorized', { status: 401 })
  }

  return NextResponse.json({ userId, data: 'Protected data' })
}
