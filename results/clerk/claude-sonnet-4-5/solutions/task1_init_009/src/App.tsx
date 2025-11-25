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
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '40px',
        borderBottom: '1px solid #eee',
        paddingBottom: '20px'
      }}>
        <h1>Welcome to Your App</h1>
        
        {/* Show UserButton when signed in */}
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
        
        {/* Show SignInButton when signed out */}
        <SignedOut>
          <SignInButton mode="modal">
            <button style={{
              padding: '10px 20px',
              backgroundColor: '#0070f3',
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
            <h2>This app uses Clerk authentication</h2>
            <p>Please sign in to access the application.</p>
            <ul style={{ marginTop: '20px' }}>
              <li>✅ Secure authentication</li>
              <li>✅ User management</li>
              <li>✅ Session handling</li>
              <li>✅ Multi-factor authentication support</li>
            </ul>
          </div>
        </SignedOut>
      </main>
    </div>
  );
}

export default App;

## Step 6: Create TypeScript Declaration File (Optional but Recommended)