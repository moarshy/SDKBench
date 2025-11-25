import type { UserResource } from '@clerk/types'

// Custom type for user profile data
export interface UserProfileData {
  id: string
  fullName: string | null
  username: string | null
  email: string | null
  imageUrl: string
  createdAt: Date
  lastSignInAt: Date | null
}

// Helper function to extract user data
export function extractUserData(user: UserResource): UserProfileData {
  return {
    id: user.id,
    fullName: user.fullName,
    username: user.username,
    email: user.primaryEmailAddress?.emailAddress || null,
    imageUrl: user.imageUrl,
    createdAt: new Date(user.createdAt!),
    lastSignInAt: user.lastSignInAt ? new Date(user.lastSignInAt) : null,
  }
}

## Usage Example in a Page