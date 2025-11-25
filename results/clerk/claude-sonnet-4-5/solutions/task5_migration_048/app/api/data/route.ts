import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const { userId } = await auth()

  if (!userId) {
    return new Response('Unauthorized', { status: 401 })
  }

  return NextResponse.json({ userId, data: 'Protected data' })
}

## Key Changes Explained

### 1. **Import Change**
- **v4**: `import { getAuth } from '@clerk/nextjs/server'`
- **v5**: `import { auth } from '@clerk/nextjs/server'`

### 2. **Function Signature**
- **v4**: `getAuth(req)` - Required passing the request object
- **v5**: `auth()` - No parameters needed, automatically accesses request context
- **v5**: `auth()` is now **async** and must be awaited

### 3. **Request Parameter**
- **v4**: Required `NextRequest` parameter in the route handler
- **v5**: No need to pass request to auth function

## Additional Migration Examples

### Example 1: POST Route with Body Parsing