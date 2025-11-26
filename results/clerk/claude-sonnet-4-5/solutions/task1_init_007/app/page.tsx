import { SignInButton, SignUpButton, UserButton, SignedIn, SignedOut } from '@clerk/nextjs'

export default function Home() {
  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Welcome</h1>
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
      </div>
      
      <SignedOut>
        <div style={{ textAlign: 'center', padding: '3rem 0' }}>
          <p style={{ marginBottom: '2rem', fontSize: '1.1rem' }}>
            This app uses Clerk authentication. Please sign in to continue.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <SignInButton mode="modal">
              <button style={{ 
                padding: '0.75rem 1.5rem', 
                fontSize: '1rem',
                backgroundColor: '#6366f1',
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: 'pointer'
              }}>
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button style={{ 
                padding: '0.75rem 1.5rem', 
                fontSize: '1rem',
                backgroundColor: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: 'pointer'
              }}>
                Sign Up
              </button>
            </SignUpButton>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div style={{ 
          padding: '2rem', 
          backgroundColor: '#f0fdf4', 
          borderRadius: '0.5rem',
          border: '1px solid #86efac'
        }}>
          <h2 style={{ color: '#166534', marginBottom: '1rem' }}>
            ✓ Authentication Successful
          </h2>
          <p style={{ color: '#15803d' }}>
            You are now signed in! Clerk authentication is working correctly.
          </p>
        </div>
      </SignedIn>
    </main>
  )
}

## Setup Instructions

After implementing these changes:

1. **Install dependencies:**