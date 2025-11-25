'use client'

import { useUser, useAuth, useClerk } from '@clerk/nextjs'

/**
 * Custom hook that combines multiple Clerk hooks
 * Useful for components that need comprehensive auth state
 */
export function useClerkAuth() {
  const { isLoaded: userLoaded, isSignedIn, user } = useUser()
  const { isLoaded: authLoaded, userId, sessionId, getToken } = useAuth()
  const clerk = useClerk()

  const isLoaded = userLoaded && authLoaded

  return {
    isLoaded,
    isSignedIn,
    user,
    userId,
    sessionId,
    getToken,
    clerk,
  }
}

/**
 * Helper function to format user display name
 */
export function getUserDisplayName(user: ReturnType<typeof useUser>['user']): string {
  if (!user) return 'Guest'
  return user.fullName || user.username || user.primaryEmailAddress?.emailAddress || 'User'
}

/**
 * Helper function to check if user has a specific role
 * Requires role to be stored in publicMetadata
 */
export function hasRole(user: ReturnType<typeof useUser>['user'], role: string): boolean {
  if (!user) return false
  const userRole = user.publicMetadata?.role as string | undefined
  return userRole === role
}