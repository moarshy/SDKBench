import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const { userId } = await auth()

    // Return different data based on authentication status
    if (userId) {
      return NextResponse.json({
        message: 'Authenticated user data',
        userId,
        data: {
          premium: true,
          features: ['feature1', 'feature2', 'feature3'],
        },
      })
    }

    // Public data for non-authenticated users
    return NextResponse.json({
      message: 'Public data',
      data: {
        premium: false,
        features: ['feature1'],
      },
    })
  } catch (error) {
    console.error('Error in data API:', error)
    return NextResponse.json