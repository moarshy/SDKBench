import { 
  SignedIn, 
  SignedOut, 
  SignInButton, 
  UserButton,
  useUser 
} from '@clerk/clerk-react';

function App() {
  const { user, isLoaded } = useUser();

  // Show loading state while Clerk is initializing
  if (!isLoaded) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px',
        borderBottom: '1px solid #ccc',
        paddingBottom: '10px'
      }}>
        <h1>Welcome to Clerk Authentication</h1>
        
        {/* Show UserButton when signed in */}
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
        
        {/* Show SignInButton when signed out */}
        <SignedOut>
          <SignInButton mode="modal">
            <button style={{
              padding: '10px 20px',
              backgroundColor: '#6C47FF',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}>
              Sign In
            </button>
          </SignInButton>
        </SignedOut>
      </header>

      <main>
        {/* Content visible only when signed in */}
        <SignedIn>
          <div>
            <h2>Hello, {user?.firstName || 'User'}! 👋</h2>
            <p>You are successfully authenticated with Clerk.</p>
            <div style={{ 
              marginTop: '20px', 
              padding: '15px', 
              backgroundColor: '#f5f5f5',
              borderRadius: '5px'
            }}>
              <h3>User Information:</h3>
              <p><strong>Email:</strong> {user?.primaryEmailAddress?.emailAddress}</p>
              <p><strong>User ID:</strong> {user?.id}</p>
            </div>
          </div>
        </SignedIn>

        {/* Content visible only when signed out */}
        <SignedOut>
          <div>
            <h2>Please sign in to continue</h2>
            <p>This app uses Clerk authentication to protect your data.</p>
            <p>Click the "Sign In" button above to get started.</p>
          </div>
        </SignedOut>
      </main>
    </div>
  );
}

export default App;

## Step 6: Create a TypeScript declaration file (optional but recommended)