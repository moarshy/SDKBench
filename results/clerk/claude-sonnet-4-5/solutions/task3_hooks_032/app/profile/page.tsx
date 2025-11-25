import UserProfile from '@/components/UserProfile'

export default function ProfilePage() {
  return (
    <main className="container mx-auto py-8">
      <UserProfile />
    </main>
  )
}

## Key Features Implemented:

1. **useAuth Hook**: Access authentication state (userId, sessionId, signOut)
2. **useUser Hook**: Access full user data and profile information
3. **Loading States**: Proper handling while data is being fetched
4. **Error Handling**: Graceful error states and user feedback
5. **TypeScript Types**: Full type safety with Clerk's types
6. **Conditional Rendering**: Different UI for signed-in/signed-out states
7. **User Information Display**: Avatar, email, phone, metadata, etc.
8. **Sign Out Functionality**: Integrated sign-out button

The component is production-ready with proper error handling, loading states, and TypeScript support!