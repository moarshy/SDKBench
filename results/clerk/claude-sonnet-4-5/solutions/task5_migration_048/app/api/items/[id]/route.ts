import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  const itemId = params.id

  return NextResponse.json({ 
    userId,
    itemId,
    data: `Item ${itemId} for user ${userId}`
  })
}

## Migration Checklist

- [x] Replace `getAuth` imports with `auth`
- [x] Remove `NextRequest` parameter from `getAuth()` calls
- [x] Add `await` to all `auth()` calls
- [x] Update error handling if needed
- [x] Test all API routes
- [x] Update TypeScript types if using custom types

## Common Pitfalls

1. **Forgetting to await**: `auth()` is async in v5