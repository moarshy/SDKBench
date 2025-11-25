import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs'
import { currentUser } from '@clerk/nextjs/server'

export default async function Home() {
  const user = await currentUser()

  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1>Welcome to Next.js with Clerk</h1>
        <p>This app is now protected with Clerk authentication.</p>
      </div>

      {user ? (
        <div>
          <div style={{ marginBottom: '1rem' }}>
            <p>
              Hello, {user.firstName || user.emailAddresses[0].emailAddress}!
            </p>
            <p>You are signed in.</p>
          </div>
          <UserButton afterSignOutUrl="/" />
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '1rem' }}>
          <SignInButton mode="modal">
            <button
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#0070f3',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
              }}
            >
              Sign In
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
              }}
            >
              Sign Up
            </button>
          </SignUpButton>
        </div>
      )}
    </main>
  )
}

## Step 6: Update package.json