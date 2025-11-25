import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const { userId } = await auth()

  if (!userId) {
    return new Response('Unauthorized', { status: 401 })
  }

  return NextResponse.json({ userId, data: 'Protected data' })
}

## Key Changes in Clerk v5:

1. **Import Change**: `getAuth` from `@clerk/nextjs/server` is replaced with `auth`
2. **Async Function**: `auth()` is now an async function that must be awaited
3. **No Request Parameter**: The `auth()` function no longer requires the `req` parameter - it automatically accesses the request context
4. **Route Handler Signature**: The `GET` function no longer needs the `req: NextRequest` parameter since we're not using it directly

## Additional Notes:

- The `auth()` function in v5 returns the same object structure with `userId`, `sessionId`, `orgId`, etc.
- Error handling remains the same - checking for `userId` to determine authentication status
- The response format is unchanged, maintaining backward compatibility for API consumers
- If you need access to other auth properties, you can destructure them: `const { userId, sessionId, orgId } = await auth()`

This migration maintains the same functionality while following Clerk v5's new patterns and conventions.