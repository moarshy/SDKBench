import { auth } from '@clerk/nextjs/server'
import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs'
import Link from 'next/link'

export default async function Home() {
  const { userId } = auth()

  return (
    <div className="min-h-screen p-8">
      <nav className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">My App</h1>
        <div className="flex gap-4 items-center">
          {userId ? (
            <>
              <Link href="/dashboard" className="text-blue-600 hover:underline">
                Dashboard
              </Link>
              <UserButton afterSignOutUrl="/" />
            </>
          ) : (
            <>
              <SignInButton mode="modal">
                <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                  Sign Up
                </button>
              </SignUpButton>
            </>
          )}
        </div>
      </nav>

      <main>
        <h2 className="text-3xl font-bold mb-4">Welcome!</h2>
        {userId ? (
          <p>You are signed in. Visit your <Link href="/dashboard" className="text-blue-600 hover:underline">dashboard</Link>.</p>
        ) : (
          <p>Please sign in to access protected content.</p>
        )}
      </main>
    </div>
  )
}

### 9. Environment Variables