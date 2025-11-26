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
        <div style={{ 
          padding: '2rem', 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px',
          backgroundColor: '#f9fafb'
        }}>
          <h2>Get Started</h2>
          <p>This app uses Clerk authentication. Please sign in to continue.</p>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
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
          border: '1px solid #e5e7eb', 
          borderRadius: '8px',
          backgroundColor: '#f0fdf4'
        }}>
          <h2>✓ Authentication Active</h2>
          <p>You are successfully signed in with Clerk authentication!</p>
          <p style={{ marginTop: '1rem', color: '#6b7280' }}>
            Your user information is now available throughout the application.
          </p>
        </div>
      </SignedIn>
    </main>
  )
}

## Setup Instructions

After updating these files, follow these steps:

1. **Install dependencies:**