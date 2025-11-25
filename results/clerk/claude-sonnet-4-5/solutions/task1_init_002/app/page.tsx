import { SignInButton, SignUpButton, UserButton, SignedIn, SignedOut } from '@clerk/nextjs'

export default function Home() {
  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Welcome</h1>
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
      </div>
      
      <SignedOut>
        <div style={{ padding: '2rem', border: '1px solid #e0e0e0', borderRadius: '8px', textAlign: 'center' }}>
          <p style={{ marginBottom: '1.5rem' }}>This app uses Clerk authentication.</p>
          <p style={{ marginBottom: '1.5rem', color: '#666' }}>
            Please sign in or create an account to continue.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <SignInButton mode="modal">
              <button style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#0070f3',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '1rem'
              }}>
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#24292e',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '1rem'
              }}>
                Sign Up
              </button>
            </SignUpButton>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div style={{ padding: '2rem', border: '1px solid #e0e0e0', borderRadius: '8px' }}>
          <h2 style={{ marginBottom: '1rem' }}>🎉 You're signed in!</h2>
          <p style={{ color: '#666' }}>
            Clerk authentication is now working. You can see your user profile in the top right corner.
          </p>
        </div>
      </SignedIn>
    </main>
  )
}

## Setup Instructions

After implementing these changes, follow these steps:

1. **Install dependencies:**