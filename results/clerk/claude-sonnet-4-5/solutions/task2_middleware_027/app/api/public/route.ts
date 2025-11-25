import { NextResponse } from 'next/server'

// This route is public and doesn't require authentication
export async function GET() {
  return NextResponse.json({
    message: 'This is a public endpoint',
    timestamp: new Date().toISOString(),
  })
}