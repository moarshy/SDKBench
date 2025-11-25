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
  lastSignInAt: Date | null
}

export function formatUserData(user: UserResource): UserData {
  return {
    id: user.id,
    fullName: user.fullName,
    username: user.username,
    email: user.primaryEmailAddress?.emailAddress || null,
    imageUrl: user.imageUrl,
    createdAt: new Date(user.createdAt || ''),
    lastSignInAt: user.lastSignInAt ? new Date(user.lastSignInAt) : null,
  }
}

## Custom Hook for User Data