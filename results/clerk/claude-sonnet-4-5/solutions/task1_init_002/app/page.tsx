import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs'
import { currentUser } from '@clerk/nextjs/server'

export default async function Home() {
  const user = await currentUser()

  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Welcome to Clerk Authentication</h1>
        {user ? (
          <UserButton afterSignOutUrl="/" />
        ) : (
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
        )}
      </div>

      {user ? (
        <div>
          <h2>You are signed in!</h2>
          <p>Welcome, {user.firstName || user.emailAddresses[0].emailAddress}!</p>
          <div style={{ marginTop: '1rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
            <h3>User Information:</h3>
            <ul>
              <li><strong>User ID:</strong> {user.id}</li>
              <li><strong>Email:</strong> {user.emailAddresses[0].emailAddress}</li>
              <li><strong>Name:</strong> {user.firstName} {user.lastName}</li>
            </ul>
          </div>
        </div>
      ) : (
        <div>
          <h2>This app uses Clerk authentication</h2>
          <p>Click the Sign In or Sign Up button above to get started.</p>
          <div style={{ marginTop: '1rem', padding: '1rem', background: '#f0f9ff', borderRadius: '8px' }}>
            <h3>Features:</h3>
            <ul>
              <li>Secure authentication</li>
              <li>User management</li>
              <li>Session handling</li>
              <li>Protected routes</li>
            </ul>
          </div>
        </div>
      )}
    </main>
  )
}

## Step 7: Add Global Styles (Optional)