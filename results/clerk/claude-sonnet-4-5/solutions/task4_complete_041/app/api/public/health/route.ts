import { NextResponse } from 'next/server'

// This route is public (defined in middleware)
export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
  })
}

### 11. Client Component with User Data