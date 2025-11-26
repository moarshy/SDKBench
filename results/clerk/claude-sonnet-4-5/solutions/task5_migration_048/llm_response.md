```typescript
// filepath: app/api/data/route.ts
import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const { userId } = await auth()

  if (!userId) {
    return new Response('Unauthorized', { status: 401 })
  }

  return NextResponse.json({ userId, data: 'Protected data' })
}
```

## Key Changes in Clerk v5:

1. **Import Change**: `getAuth` from `@clerk/nextjs/server` is replaced with `auth`
2. **Async Function**: `auth()` is now an async function that must be awaited
3. **No Request Parameter**: The `auth()` function no longer requires the `req` parameter - it automatically accesses the request context
4. **Simplified API**: The new approach is cleaner and follows Next.js App Router conventions better

## Additional Notes:

- The `auth()` function in v5 returns the same object structure with `userId`, `sessionId`, `orgId`, etc.
- If you need to check authentication and throw an error, you can use `auth().protect()` which will automatically throw if not authenticated
- For more user details, you can use `currentUser()` from `@clerk/nextjs/server`

## Alternative Pattern (with protect):

If you want automatic protection without manual checks:

```typescript
import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const { userId } = await auth.protect()
  
  // This line only runs if authenticated
  return NextResponse.json({ userId, data: 'Protected data' })
}
```

The `protect()` method will automatically return a 401 response if the user is not authenticated.