import { NextResponse } from 'next/server'

// This route is public as defined in middleware
export async function GET() {
  return NextResponse.json({ 
    message: 'This is a public API endpoint',
    timestamp: new Date().toISOString()
  })
}