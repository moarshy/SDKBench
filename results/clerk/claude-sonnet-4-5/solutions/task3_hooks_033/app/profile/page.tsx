import UserProfile from '@/components/UserProfile';

export default function ProfilePage() {
  return <UserProfile />;
}

## Key Features Implemented:

1. **useUser Hook**: Access user data, loading state, and sign-in status
2. **useAuth Hook**: Access authentication state, session info, and tokens
3. **useClerk Hook**: Access Clerk methods like signOut and openUserProfile
4. **Loading States**: Proper skeleton/spinner while data loads
5. **Error Handling**: Graceful handling of missing data
6. **TypeScript Types**: Full type safety with Clerk's built-in types
7.