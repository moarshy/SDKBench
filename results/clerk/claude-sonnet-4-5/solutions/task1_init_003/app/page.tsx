import { SignInButton, SignUpButton, UserButton, SignedIn, SignedOut } from '@clerk/nextjs'
import { currentUser } from '@clerk/nextjs/server'

export default async function Home() {
  // Get the current user on the server side
  const user = await currentUser()

  return (
    <main>
      <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
        <h1>Welcome to Next.js with Clerk</h1>
        
        <div style={{ marginTop: '2rem' }}>
          {/* Show sign in/up buttons when signed out */}
          <SignedOut>
            <p>Please sign in to continue</p>
            <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
              <SignInButton mode="modal">
                <button style={{ 
                  padding: '0.5rem 1rem', 
                  cursor: 'pointer',
                  backgroundColor: '#0070f3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px'
                }}>
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button style={{ 
                  padding: '0.5rem 1rem', 
                  cursor: 'pointer',
                  backgroundColor: '#24292e',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px'
                }}>
                  Sign Up
                </button>
              </SignUpButton>
            </div>
          </SignedOut>

          {/* Show user info when signed in */}
          <SignedIn>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <p>Welcome back, {user?.firstName || user?.emailAddresses[0]?.emailAddress}!</p>
              <UserButton afterSignOutUrl="/" />
            </div>
            <p style={{ marginTop: '1rem', color: '#666' }}>
              You are now authenticated with Clerk.
            </p>
          </SignedIn>
        </div>
      </div>
    </main>
  )
}

## Step 8: Create Sign In and Sign Up Pages (Optional)

If you want dedicated pages instead of modals: