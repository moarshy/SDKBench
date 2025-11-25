import { 
  SignedIn, 
  SignedOut, 
  SignInButton, 
  UserButton,
  useUser 
} from '@clerk/clerk-react';
import { useState, useEffect } from 'react';

function App() {
  const { user, isLoaded } = useUser();
  const [protectedData, setProtectedData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchProtectedData = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/protected', {
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch protected data');
      }
      
      const data = await response.json();
      setProtectedData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  return (
    <div className="app">
      <header>
        <h1>Clerk + Express App</h1>
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
      </header>

      <main>
        <SignedOut>
          <div className="sign-in-container">
            <h2>Welcome! Please sign in</h2>
            <SignInButton mode="modal">
              <button className="sign-in-button">Sign In</button>
            </SignInButton>
          </div>
        </SignedOut>

        <SignedIn>
          <div className="user-info">
            <h2>Welcome, {user?.firstName || 'User'}!</h2>
            <p>Email: {user?.primaryEmailAddress?.emailAddress}</p>
            
            <button onClick={fetchProtectedData}>
              Fetch Protected Data
            </button>

            {protectedData && (
              <div className="protected-data">
                <h3>Protected Data:</h3>
                <pre>{JSON.stringify(protectedData, null, 2)}</pre>
              </div>
            )}

            {error && (
              <div className="error">
                <p>Error: {error}</p>
              </div>
            )}
          </div>
        </SignedIn>
      </main>
    </div>
  );
}

export default App;