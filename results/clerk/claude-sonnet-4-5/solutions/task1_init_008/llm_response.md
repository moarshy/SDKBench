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

# Optional: Custom sign-in/sign-up URLs
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Welcome</h1>
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
      </div>
      
      <SignedOut>
        <div style={{ textAlign: 'center', padding: '3rem 0' }}>
          <p style={{ marginBottom: '2rem', fontSize: '1.1rem' }}>
            This app uses Clerk authentication. Please sign in to continue.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <SignInButton mode="modal">
              <button style={{ 
                padding: '0.75rem 1.5rem', 
                fontSize: '1rem',
                backgroundColor: '#6366f1',
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: 'pointer'
              }}>
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button style={{ 
                padding: '0.75rem 1.5rem', 
                fontSize: '1rem',
                backgroundColor: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: 'pointer'
              }}>
                Sign Up
              </button>
            </SignUpButton>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div style={{ 
          padding: '2rem', 
          backgroundColor: '#f0fdf4', 
          borderRadius: '0.5rem',
          border: '1px solid #86efac'
        }}>
          <h2 style={{ color: '#166534', marginBottom: '1rem' }}>✓ Authentication Active</h2>
          <p style={{ color: '#15803d' }}>
            You are now signed in! Clerk is successfully integrated into your application.
          </p>
        </div>
      </SignedIn>
    </main>
  )
}
```

## Setup Instructions

After applying these changes:

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create a `.env.local` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env.local
   ```

3. **Get your Clerk keys:**
   - Go to https://dashboard.clerk.com
   - Create a new application (or select existing)
   - Copy your publishable key and secret key
   - Paste them into `.env.local`

4. **Run the development server:**
   ```bash
   npm run dev
   ```

5. **Test the integration:**
   - Visit http://localhost:3000
   - Click "Sign In" or "Sign Up"
   - Complete the authentication flow
   - You should see the authenticated state

## What Changed

1. **package.json**: Added `@clerk/nextjs` v5.0.0 dependency
2. **.env.example**: Added required Clerk environment variables with examples
3. **app/layout.tsx**: Wrapped the app with `ClerkProvider` to enable authentication context
4. **app/page.tsx**: Added Clerk components to demonstrate authentication UI:
   - `SignedIn`/`SignedOut`: Conditional rendering based on auth state
   - `SignInButton`/`SignUpButton`: Authentication triggers
   - `UserButton`: User profile menu when signed in

The application is now fully initialized with Clerk authentication!