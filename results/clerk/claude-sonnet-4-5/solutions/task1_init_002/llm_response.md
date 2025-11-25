I'll help you initialize Clerk authentication in your Next.js application. Here's the complete solution:

```json
// filepath: package.json
{
  "name": "nextjs-app",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "^14.0.0",
    "@clerk/nextjs": "^5.0.0"
  }
}
```

```bash
# filepath: .env.example
# Clerk Authentication Keys
# Get these from https://dashboard.clerk.com
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Custom sign-in/sign-up URLs (if using custom pages)
# NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
# NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
# NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
# NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
```

```tsx
// filepath: app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs'
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}
```

```tsx
// filepath: app/page.tsx
import { SignInButton, SignUpButton, UserButton, SignedIn, SignedOut } from '@clerk/nextjs'

export default function Home() {
  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Welcome</h1>
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
      </div>
      
      <SignedOut>
        <div style={{ padding: '2rem', border: '1px solid #e0e0e0', borderRadius: '8px', textAlign: 'center' }}>
          <p style={{ marginBottom: '1.5rem' }}>This app uses Clerk authentication.</p>
          <p style={{ marginBottom: '1.5rem', color: '#666' }}>
            Please sign in or create an account to continue.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <SignInButton mode="modal">
              <button style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#0070f3',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '1rem'
              }}>
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#24292e',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '1rem'
              }}>
                Sign Up
              </button>
            </SignUpButton>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div style={{ padding: '2rem', border: '1px solid #e0e0e0', borderRadius: '8px' }}>
          <h2 style={{ marginBottom: '1rem' }}>🎉 You're signed in!</h2>
          <p style={{ color: '#666' }}>
            Clerk authentication is now working. You can see your user profile in the top right corner.
          </p>
        </div>
      </SignedIn>
    </main>
  )
}
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
   - Copy your API keys

3. **Set up environment variables:**
   - Create a `.env.local` file in your project root
   - Copy the contents from `.env.example`
   - Replace the placeholder values with your actual Clerk keys

4. **Run the development server:**
   ```bash
   npm run dev
   ```

5. **Test the authentication:**
   - Visit http://localhost:3000
   - Click "Sign In" or "Sign Up" to test the authentication flow
   - The UserButton will appear in the top right after signing in

## What's Been Implemented

✅ **ClerkProvider** wraps the entire application in `app/layout.tsx`
✅ **Clerk v5** package added to dependencies
✅ **Environment variables** configured in `.env.example`
✅ **Authentication UI components** added to the home page:
  - `SignInButton` - Opens sign-in modal
  - `SignUpButton` - Opens sign-up modal
  - `UserButton` - Shows user profile menu when signed in
  - `SignedIn` - Renders content only for authenticated users
  - `SignedOut` - Renders content only for unauthenticated users

The application is now ready for Clerk authentication! Users can sign in/up using the modal dialogs, and the UI will automatically update based on their authentication state.