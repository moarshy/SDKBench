import { NextResponse } from 'next/server'

export async function GET() {
  // This route is public and doesn't require authentication
  return NextResponse.json({
    message: 'This is a public API route',
    timestamp: new Date().toISOString(),
    public: true,
  })
}

### 5. Create Sign-In Page