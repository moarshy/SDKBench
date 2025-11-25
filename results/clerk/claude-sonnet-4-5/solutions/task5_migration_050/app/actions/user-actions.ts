'use server'

import { auth, currentUser } from '@clerk/nextjs/server'
import { revalidatePath } from 'next/cache'

export async function updateUserPreferences(preferences: any) {
  const { userId } = auth()

  if (!userId) {
    throw new Error('Unauthorized')
  }

  // Your database logic here
  // await db.userPreferences.update({ userId, ...preferences })

  revalidatePath('/settings')
  return { success: true }
}

export async function getUserData() {
  const user = await currentUser()

  if (!user) {
    throw new Error('Unauthorized')
  }

  return {
    id: user.id,
    email: user.emailAddresses[0]?.emailAddress,
    name: `${user.firstName} ${user.lastName}`,
  }
}

## Key Breaking Changes Summary

| Clerk v4 | Clerk v5 |
|----------|----------|
| `@clerk/nextjs/app-beta` | `@clerk/nextjs/server` |
| `authMiddleware()` | `clerkMiddleware()` |
| `redirectToSignIn()` | `auth().protect()` or manual redirect |

## Migration Checklist

- [x] Update `@clerk/nextjs` to version 5.0.0
- [x] Change import from `@clerk/nextjs/app-beta` to `@clerk/nextjs/server`
- [x] Update middleware from `authMiddleware()` to `clerkMiddleware()`
- [x] Verify environment variables are set correctly
- [x] Test authentication flow
- [x] Test protected routes
- [x] Test API routes with authentication
- [x] Update any custom authentication logic

## Testing Your Migration

After migration, test these scenarios:

1. **Unauthenticated access**: Visit `/profile` without signing in
2. **Authenticated access**: Sign in and visit `/profile`
3. **Middleware protection**: Try accessing protected routes
4. **API routes**: Test authenticated API endpoints
5. **Sign out**: Ensure sign out works correctly

The migration is complete! Your server components will now use the correct Clerk v5 imports and patterns.