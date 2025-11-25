import { SignInButton, SignUpButton, UserButton, SignedIn, SignedOut } from '@clerk/nextjs'

export default function Home() {
  return (
    <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Welcome</h1>
        <div>
          <SignedOut>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <SignInButton mode="modal">
                <button style={{ padding: '0.5rem 1rem', cursor: 'pointer' }}>
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button style={{ padding: '0.5rem 1rem', cursor: 'pointer' }}>
                  Sign Up
                </button>
              </SignUpButton>
            </div>
          </SignedOut>
          <SignedIn>
            <UserButton afterSignOutUrl="/" />
          </SignedIn>
        </div>
      </div>
      
      <SignedOut>
        <p>This app uses Clerk authentication. Please sign in to continue.</p>
      </SignedOut>
      
      <SignedIn>
        <p>You are now signed in! 🎉</p>
        <p>You have access to protected content.</p>
      </SignedIn>
    </main>
  )
}

## Step 7: Create Global Styles (Optional)