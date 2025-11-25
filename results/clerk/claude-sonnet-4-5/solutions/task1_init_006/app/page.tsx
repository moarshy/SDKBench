import { SignInButton, SignUpButton, UserButton, SignedIn, SignedOut } from '@clerk/nextjs'
import { currentUser } from '@clerk/nextjs/server'

export default async function Home() {
  // Get the current user on the server side
  const user = await currentUser()

  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Welcome to Clerk Authentication</h1>
        
        {/* Show user button when signed in */}
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
        
        {/* Show sign in/up buttons when signed out */}
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
      </div>

      <SignedOut>
        <p>This app uses Clerk authentication. Please sign in to continue.</p>
      </SignedOut>

      <SignedIn>
        <div>
          <h2>You are signed in!</h2>
          {user && (
            <div style={{ marginTop: '1rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
              <p><strong>User ID:</strong> {user.id}</p>
              <p><strong>Email:</strong> {user.emailAddresses[0]?.emailAddress}</p>
              <p><strong>Name:</strong> {user.firstName} {user.lastName}</p>
            </div>
          )}
        </div>
      </SignedIn>
    </main>
  )
}

## Step 7: Create Global Styles (Optional)