'use client'

import { useUser } from '@clerk/nextjs'
import { useMemo } from 'react'

export interface UseUserDataReturn {
  isLoading: boolean
  isSignedIn: boolean
  user: {
    id: string
    fullName: string
    username: string
    email: string
    imageUrl: string
    createdAt: string
    lastSignInAt: string | null
  } | null
  error: Error | null
}

export function useUserData(): UseUserDataReturn {
  const { isLoaded, isSignedIn, user } = useUser()

  const userData = useMemo(() => {
    if (!user)