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
# Get these from your Clerk Dashboard: https://dashboard.clerk.com
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here

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
        <div style={{ padding: '2rem', border: '1px solid #e0e0e0', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
          <h2>This app uses Clerk authentication</h2>
          <p style={{ marginBottom: '1.5rem' }}>
            Please sign in to access the application features.
          </p>
          <div style={{ display: 'flex', gap: '1rem' }}>
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
        <div style={{ padding: '2rem', border: '1px solid #e0e0e0', borderRadius: '8px', backgroundColor: '#f0f9ff' }}>
          <h2>🎉 You're signed in!</h2>
          <p>
            Clerk authentication is now active. You can access protected features and your user profile.
          </p>
        </div>
      </SignedIn>
    </main>
  )
}
```

## Setup Instructions

After updating these files, follow these steps:

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

## What's Been Added

1. **ClerkProvider**: Wraps the entire application in `app/layout.tsx` to provide authentication context
2. **Clerk Components**: Added `SignInButton`, `SignUpButton`, `UserButton`, `SignedIn`, and `SignedOut` to the home page
3. **Environment Variables**: Configured the required Clerk API keys in `.env.example`
4. **Package Dependency**: Added `@clerk/nextjs` version 5.0.0 to `package.json`

The application now has a fully functional authentication system with sign-in/sign-up modals and user profile management!