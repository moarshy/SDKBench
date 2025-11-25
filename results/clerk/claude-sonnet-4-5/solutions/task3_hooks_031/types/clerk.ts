import { UserResource } from '@clerk/types'

export interface UserProfileProps {
  className?: string
}

export interface UserData {
  id: string
  fullName: string | null
  username: string | null
  email: string | null
  imageUrl: string
  createdAt: Date
}

// Helper function to extract user data
export function extractUserData(user: UserResource): UserData {
  return {
    id: user.id,
    fullName: user.fullName,
    username: user.username,
    email: user.primaryEmailAddress?.emailAddress || null,
    imageUrl: user.imageUrl,
    createdAt: new Date(user.createdAt!),
  }
}

## Usage Example in a Page