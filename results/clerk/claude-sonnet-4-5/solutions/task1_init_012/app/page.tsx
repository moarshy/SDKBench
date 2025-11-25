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
          <h2>Hello, {user.firstName || user.emailAddresses[0].emailAddress}!</h2>
          <p>You are successfully authenticated with Clerk.</p>
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
          <p>This app uses Clerk for authentication.</p>
          <p>Click the buttons above to sign in or create an account.</p>
        </div>
      )}
    </main>
  )
}

## Step 7: Add Global Styles (Optional)