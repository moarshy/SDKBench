import { UserResource } from '@clerk/types'

// Extend if you need custom types
export interface ExtendedUserData extends UserResource {
  // Add any custom fields here
}

// Example usage in component
export interface UserProfileProps {
  showEmail?: boolean
  showPhone?: boolean
  onSignOut?: () => void
}

## Key Points:

1. **useAuth Hook**: Provides authentication state (`userId`, `sessionId`, `isLoaded`, `signOut`)
2. **useUser Hook**: Provides user data (`user`, `isSignedIn`, `isLoaded`)
3. **Loading States**: Always check `isLoaded` before accessing data
4. **Client Component**: Must use `'use client'` directive for hooks
5. **Error Handling**: Check for null/undefined values
6. **TypeScript**: Clerk provides full type definitions out of the box

The component is now production-ready with proper loading states, error handling, and displays comprehensive user information from Clerk!