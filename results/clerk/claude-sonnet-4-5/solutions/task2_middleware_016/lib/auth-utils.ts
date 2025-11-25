import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

/**
 * Utility function to require authentication in server components
 * Redirects to sign-in if not authenticated
 */
export async function requireAuth() {
  const { userId } = await auth()
  
  if (!userId) {
    redirect('/sign-in')
  }
  
  return userId
}

/**
 * Utility function to get optional auth state
 * Returns userId or null without redirecting
 */
export async function getOptionalAuth() {
  const { userId } = await auth()
  return userId
}