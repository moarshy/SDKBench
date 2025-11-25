import { NextResponse } from 'next/server'

export async function GET() {
  // This route is public and doesn't require authentication
  return NextResponse.json({ 
    message: 'This is a public endpoint',
    timestamp: new Date().toISOString()
  })
}

### 7. Update Root Layout