import { NextResponse } from 'next/server'

// This route is public (defined in middleware)
export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    message: 'This is a public endpoint',
  })
}

### 12. Client Component Example with Hooks