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
        <div style={{ padding: '2rem', border: '1px solid #e0e0e0', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
          <h2>This app uses Clerk authentication</h2>
          <p style={{ marginBottom: '1.5rem' }}>
            Please sign in to access the application features.
          </p>
          <div style={{ display: 'flex', gap: '1rem' }}>
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
        <div style={{ padding: '2rem', border: '1px solid #e0e0e0', borderRadius: '8px', backgroundColor: '#f0f9ff' }}>
          <h2>🎉 You're signed in!</h2>
          <p>
            Clerk authentication is now active. You can access protected features and your user profile.
          </p>
        </div>
      </SignedIn>
    </main>
  )
}

## Setup Instructions

After updating these files, follow these steps:

1. **Install dependencies:**