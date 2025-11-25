import { SignInButton, SignUpButton, UserButton, SignedIn, SignedOut } from '@clerk/nextjs'
import { currentUser } from '@clerk/nextjs/server'

export default async function Home() {
  // Get the current user on the server side
  const user = await currentUser()

  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Welcome to Next.js with Clerk</h1>
        
        {/* Show UserButton when signed in */}
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
        <div style={{ padding: '2rem', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
          <h2>Authentication Required</h2>
          <p>Please sign in to access this application.</p>
        </div>
      </SignedOut>

      <SignedIn>
        <div style={{ padding: '2rem', backgroundColor: '#e8f5e9', borderRadius: '8px' }}>
          <h2>You are signed in!</h2>
          {user && (
            <div>
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

## Step 7: Create Optional Custom Sign-In/Sign-Up Pages