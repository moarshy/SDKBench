import UserProfile from '@/components/UserProfile'

export default function ProfilePage() {
  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <UserProfile />
    </main>
  )
}

## Key Features Implemented:

1. **useAuth Hook**: Access authentication state (userId, sessionId, signOut)
2. **useUser Hook**: Access user data and profile information
3. **Loading States**: Proper handling while data is being fetched
4. **Error Handling**: Graceful error messages and fallbacks
5. **TypeScript Types**: Full type safety with Clerk's built-in types
6. **Sign In/Out**: Integration with Clerk's authentication buttons
7. **Responsive Design**: Clean, professional UI with Tailwind CSS
8. **Data Refresh**: Ability to reload user data on demand

All implementations are production-ready and follow Clerk v5 best practices!