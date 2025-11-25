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

# Optional: Custom URLs for sign-in and sign-up pages
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
```

## Setup Instructions

After implementing these changes:

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create a `.env` file** in your project root (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

3. **Get your Clerk keys:**
   - Go to [Clerk Dashboard](https://dashboard.clerk.com)
   - Create a new application or select an existing one
   - Copy your Publishable Key from the API Keys section
   - Add it to your `.env` file

4. **Start your application:**
   ```bash
   npm start
   ```

## What's Been Added

1. **ClerkProvider**: Wraps the entire application to provide authentication context
2. **Environment Variables**: Configured for Clerk publishable key
3. **Error Handling**: Throws an error if the publishable key is missing
4. **UI Components**: Added `SignedIn`, `SignedOut`, `SignInButton`, and `UserButton` components to demonstrate authentication state
5. **Type Safety**: Maintained TypeScript support throughout

The application is now ready to use Clerk authentication! Users can sign in using the modal, and the UI will automatically update based on their authentication state.