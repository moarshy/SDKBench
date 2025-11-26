import React from 'react';
import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton,
  useUser
} from '@clerk/clerk-react';
import './App.css';

function App() {
  const { user, isLoaded } = useUser();

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
          <div className="auth-section">
            <p>Please sign in to continue</p>
            <SignInButton mode="modal">
              <button className="sign-in-button">Sign In</button>
            </SignInButton>
          </div>
        </SignedOut>

        <SignedIn>
          <div className="user-section">
            <p>Welcome, {user?.firstName || user?.username || 'User'}!</p>
            <UserButton afterSignOutUrl="/" />
            <div className="user-info">
              <h3>User Information:</h3>
              <p>Email: {user?.primaryEmailAddress?.emailAddress}</p>
              <p>User ID: {user?.id}</p>
            </div>
          </div>
        </SignedIn>
      </header>
    </div>
  );
}

export default App;