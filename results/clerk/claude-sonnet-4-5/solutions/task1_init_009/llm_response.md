I'll help you initialize Clerk authentication in your React application. Here's the complete solution:

```json
// filepath: package.json
{
  "name": "react-app",
  "version": "0.1.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@clerk/clerk-react": "^5.0.0"
  }
}
```

```env
// filepath: .env.example
# Clerk Authentication Keys
# Get these from your Clerk Dashboard: https://dashboard.clerk.com
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Optional: Custom sign-in/sign-up URLs (if using custom pages)
# REACT_APP_CLERK_SIGN_IN_URL=/sign-in
# REACT_APP_CLERK_SIGN_UP_URL=/sign-up
# REACT_APP_CLERK_AFTER_SIGN_IN_URL=/
# REACT_APP_CLERK_AFTER_SIGN_UP_URL=/
```

```tsx
// filepath: src/index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { ClerkProvider } from '@clerk/clerk-react';
import App from './App';

// Get the publishable key from environment variables
const clerkPubKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

if (!clerkPubKey) {
  throw new Error('Missing Clerk Publishable Key. Please add REACT_APP_CLERK_PUBLISHABLE_KEY to your .env file');
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ClerkProvider publishableKey={clerkPubKey}>
      <App />
    </ClerkProvider>
  </React.StrictMode>
);
```

```tsx
// filepath: src/App.tsx
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
          <p>✅ You are signed in! Clerk authentication is working.</p>
        </SignedIn>
        <SignedOut>
          <p>This app uses Clerk authentication. Please sign in to continue.</p>
        </SignedOut>
      </main>
    </div>
  );
}

export default App;
```

## Setup Instructions

After implementing these changes, follow these steps:

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create a Clerk account and application:**
   - Go to https://dashboard.clerk.com
   - Create a new application
   - Copy your Publishable Key

3. **Create a `.env` file:**
   ```bash
   cp .env.example .env
   ```

4. **Add your Clerk key to `.env`:**
   ```env
   REACT_APP_CLERK_PUBLISHABLE_KEY=pk_test_your_actual_key_here
   ```

5. **Start your application:**
   ```bash
   npm start
   ```

## What's Been Added

1. **ClerkProvider**: Wraps the entire application to provide authentication context
2. **Environment Variables**: Configured for the Clerk publishable key
3. **Error Handling**: Throws an error if the publishable key is missing
4. **UI Components**: Added `SignedIn`, `SignedOut`, `SignInButton`, and `UserButton` to demonstrate authentication state
5. **Package Dependency**: Added `@clerk/clerk-react` version 5.0.0

The application now has a complete Clerk authentication setup with a working sign-in flow!