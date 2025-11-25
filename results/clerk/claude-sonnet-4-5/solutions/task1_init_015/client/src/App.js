import React from 'react';
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton,
  useUser,
  useAuth
} from '@clerk/clerk-react';
import './App.css';

function App() {
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();

  const fetchProtectedData = async () => {
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:3001/api/protected', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      const data = await response.json();
      console.log('Protected data:', data);
      alert(JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Error fetching protected data:', error);
      alert('Error: ' + error.message);
    }
  };

  if (!isLoaded) {
    return (
      <div className="App">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Clerk + Express Authentication</h1>
        
        <SignedOut>
          <div className="auth-buttons">
            <p>Please sign in to continue</p>
            <SignInButton mode="modal">
              <button className="btn btn-primary">Sign In</button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="btn btn-secondary">Sign Up</button>
            </SignUpButton>
          </div>
        </SignedOut>

        <SignedIn>
          <div className="user-section">
            <div className="user-info">
              <UserButton afterSignOutUrl="/" />
              <div className="user-details">
                <p>Welcome, {user?.firstName || user?.username || 'User'}!</p>
                <p className="user-email">{user?.primaryEmailAddress?.emailAddress}</p>
              </div>
            </div>
            
            <div className="actions">
              <button 
                className="btn btn-primary"
                onClick={fetchProtectedData}
              >
                Test Protected Route
              </button>
            </div>
          </div>
        </SignedIn>
      </header>
    </div>
  );
}

export default App;