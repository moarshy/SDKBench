import { NextResponse } from 'next/server'

// This is a public API route that doesn't require authentication
export async function GET() {
  return NextResponse.json({
    message: 'This is a public API route',
    timestamp: new Date().toISOString(),
  })
}