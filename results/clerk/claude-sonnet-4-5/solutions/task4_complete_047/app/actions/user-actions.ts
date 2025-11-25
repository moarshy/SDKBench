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
  // Example: await db.userPreferences.update({ userId, ...preferences })

  revalidatePath('/dashboard')
  
  return { success: true }
}

### 13. Global CSS (Optional Styling)