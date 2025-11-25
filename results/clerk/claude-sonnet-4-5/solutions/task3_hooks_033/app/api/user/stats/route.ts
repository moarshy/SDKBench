import { auth } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

export async function GET() {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Example: Fetch stats from your database
  const stats = {
    sessionCount: 42,
    lastActive: new Date().toISOString(),
  };

  return NextResponse.json(stats);
}

## Usage Example