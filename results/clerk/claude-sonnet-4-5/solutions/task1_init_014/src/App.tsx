import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';

function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Welcome</h1>
        <SignedIn>
          {/* Show user button when signed in */}
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
        <SignedOut>
          {/* Show sign in button when signed out */}
          <SignInButton mode="modal">
            <button style={{ padding: '10px 20px', cursor: 'pointer' }}>
              Sign In
            </button>
          </SignInButton>
        </SignedOut>
      </header>

      <main>
        <SignedIn>
          <p>✅ You are now authenticated with Clerk!</p>
          <p>You can now access protected features of this application.</p>
        </SignedIn>
        <SignedOut>
          <p>This app uses Clerk authentication.</p>
          <p>Please sign in to continue.</p>
        </SignedOut>
      </main>
    </div>
  );
}

export default App;

## Setup Instructions

After applying these changes, follow these steps:

1. **Install dependencies:**