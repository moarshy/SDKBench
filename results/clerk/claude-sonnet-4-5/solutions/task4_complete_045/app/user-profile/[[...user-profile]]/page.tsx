import { UserProfile } from '@clerk/nextjs'

export default function UserProfilePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <UserProfile 
        appearance={{
          elements: {
            rootBox: "mx-auto",
            card: "shadow-lg"
          }
        }}
        routing="path"
        path="/user-profile"
      />
    </div>
  )
}