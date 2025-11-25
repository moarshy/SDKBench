import { NextResponse } from 'next/server'

export async function GET() {
  // TODO: Protect this API route
  return NextResponse.json({ message: 'User data' })
}
