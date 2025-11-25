'use server'

import { auth, currentUser } from '@clerk/nextjs/server'
import { revalidatePath } from 'next/cache'

export async function getUserData() {
  const { userId } = await auth()
  
  if (!userId) {
    throw new Error('Unauthorized')
  }

  const user = await currentUser()
  
  return {
    id: userId,
    email: user?.emailAddresses[0]?.emailAddress,
    firstName: user?.firstName,
    lastName: user?.lastName,
  }
}

export async function updateUserPreferences(preferences: any) {
  const { userId } = await auth()
  
  if (!userId) {
    throw new Error('Unauthorized')
  }

  // Update user preferences in your database
  // This is just an example
  console.log('Updating preferences for user:', userId, preferences)

  revalidatePath('/dashboard')
  
  return { success: true }
}

### 14. TypeScript Configuration