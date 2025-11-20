import { NextResponse } from 'next/server'

export async function GET() {
  // TODO: This API route should be protected
  return NextResponse.json({ message: 'This should be protected' })
}
