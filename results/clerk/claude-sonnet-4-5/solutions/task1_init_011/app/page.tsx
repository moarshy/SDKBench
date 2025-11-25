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
        <div style={{ 
          padding: '2rem', 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px',
          backgroundColor: '#f9fafb'
        }}>
          <h2>Authentication Required</h2>
          <p>This app uses Clerk authentication. Please sign in to continue.</p>
          <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
            <SignInButton mode="modal">
              <button style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#2563eb',
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
                padding: '0.5rem 1rem',
                backgroundColor: '#059669',
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
        <div style={{ 
          padding: '2rem', 
          border: '1px solid #d1fae5', 
          borderRadius: '8px',
          backgroundColor: '#ecfdf5'
        }}>
          <h2>✓ Authenticated</h2>
          <p>You are now signed in! Clerk authentication is working correctly.</p>
        </div>
      </SignedIn>
    </main>
  )
}

## Setup Instructions

After updating these files, follow these steps:

1. **Install dependencies:**