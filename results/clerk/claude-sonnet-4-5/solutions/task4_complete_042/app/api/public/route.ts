import { NextResponse } from 'next/server'

// This route is public (defined in middleware)
export async function GET() {
  return NextResponse.json({
    message: 'This is a public endpoint',
    timestamp: new Date().toISOString()
  })
}

### 12. Client Component with User Data