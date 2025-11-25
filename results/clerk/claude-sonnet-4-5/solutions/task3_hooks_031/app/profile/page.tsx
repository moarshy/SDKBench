import UserProfile from '@/components/UserProfile'

export default function ProfilePage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <UserProfile />
    </main>
  )
}

## Key Features Implemented:

1. ✅ **useUser Hook**: Properly integrated to access user data
2. ✅ **Loading States**: Handles the loading state while Clerk initializes
3. ✅ **Authentication Check**: Verifies if user is signed in
4. ✅ **Error Handling**: Gracefully handles unauthenticated states
5. ✅ **TypeScript Types**: Full type safety with Clerk's types
6. ✅ **User Data Display**: Shows all relevant user information
7. ✅ **Responsive Design**: Mobile-friendly layout
8. ✅ **Production Ready**: Follows best practices and conventions

The component is now fully functional and ready to use in your Next.js application with Clerk v5!