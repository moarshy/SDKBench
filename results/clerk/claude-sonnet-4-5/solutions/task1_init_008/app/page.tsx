import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'

export default function Home() {
  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Welcome to Next.js with Clerk</h1>
      
      <SignedOut>
        <div style={{ marginTop: '2rem' }}>
          <p>This app uses Clerk authentication.</p>
          <p>Please sign in to continue:</p>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <SignInButton mode="modal">
              <button style={{ 
                padding: '0.5rem 1rem', 
                backgroundColor: '#0070f3', 
                color: 'white', 
                border: 'none', 
                borderRadius: '5px',
                cursor: 'pointer'
              }}>
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button style={{ 
                padding: '0.5rem 1rem', 
                backgroundColor: '#24292e', 
                color: 'white', 
                border: 'none', 
                borderRadius: '5px',
                cursor: 'pointer'
              }}>
                Sign Up
              </button>
            </SignUpButton>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div style={{ marginTop: '2rem' }}>
          <p>You are signed in!</p>
          <div style={{ marginTop: '1rem' }}>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </SignedIn>
    </main>
  )
}

## Step 7: Create Global Styles (Optional)