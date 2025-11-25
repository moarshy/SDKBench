import type { User } from '@clerk/nextjs/server'

// The useUser hook returns:
export interface UseUserReturn {
  isLoaded: boolean
  isSignedIn: boolean | undefined
  user: User | null | undefined
}

// The useAuth hook returns:
export interface UseAuthReturn {
  isLoaded: boolean
  isSignedIn: boolean | undefined
  userId: string | null | undefined
  sessionId: string | null | undefined
  orgId: string | null | undefined
  orgRole: string | null | undefined
  orgSlug: string | null | undefined
}

## Key Points

1. **Always check `isLoaded`**: Clerk needs time to initialize, so always check this first
2. **Check `isSignedIn`**: Before accessing user data, verify the user is signed in
3. **Use 'use client'**: Clerk hooks only work in Client Components
4. **Handle null/undefined**: User data can be null or undefined, use optional chaining
5. **TypeScript support**: Clerk provides full TypeScript types out of the box

The implementation includes:
- ✅ Loading state handling
- ✅ Authentication state checking
- ✅ Comprehensive user data display
- ✅ Error-free null handling
- ✅ TypeScript types
- ✅ Production-ready styling
- ✅ Responsive design