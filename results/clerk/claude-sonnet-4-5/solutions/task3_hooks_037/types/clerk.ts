import type { UserResource } from '@clerk/types'

// The useUser hook returns:
export interface UseUserReturn {
  isLoaded: boolean
  isSignedIn: boolean | undefined
  user: UserResource | null | undefined
}

// The useAuth hook returns:
export interface UseAuthReturn {
  isLoaded: boolean
  isSignedIn: boolean | undefined
  userId: string | null | undefined
  sessionId: string | null | undefined
  actor: ActJWTClaim | null | undefined
  orgId: string | null | undefined
  orgRole: string | null | undefined
  orgSlug: string | null | undefined
  getToken: (options?: GetTokenOptions) => Promise<string | null>
  signOut: SignOutCallback
}

## Key Features Implemented

1. ✅ **Loading State**: Shows skeleton loader while Clerk initializes
2. ✅ **Not Signed In State**: Displays message when user is not authenticated
3. ✅ **User Data Display**: Shows comprehensive user information
4. ✅ **Email & Phone Verification Status**: Displays verification badges
5. ✅ **Primary Contact Indicators**: Shows which email/phone is primary
6. ✅ **Account Metadata**: Displays creation date, last sign-in, 2FA status
7. ✅ **Profile Image**: Shows user avatar with fallback
8. ✅ **TypeScript Support**: Fully typed with Clerk's types
9. ✅ **Responsive Design**: Mobile-friendly layout
10. ✅ **Error Handling**: Graceful handling of missing data

The component is production-ready and follows Clerk v5 best practices!