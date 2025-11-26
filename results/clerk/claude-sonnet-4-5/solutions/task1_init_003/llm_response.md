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
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here

# Optional: Custom sign-in/sign-up pages
# NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
# NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
# NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
# NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
```

```tsx
// filepath: app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs'
import './globals.css'

export const metadata = {
  title: 'Next.js with Clerk',
  description: 'A Next.js application with Clerk authentication',
}

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
        <div style={{ padding: '2rem', border: '1px solid #ddd', borderRadius: '8px' }}>
          <p style={{ marginBottom: '1rem' }}>This app uses Clerk authentication.</p>
          <p style={{ marginBottom: '1.5rem' }}>Please sign in to continue.</p>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <SignInButton mode="modal">
              <button style={{ 
                padding: '0.5rem 1rem', 
                backgroundColor: '#0070f3', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer'
              }}>
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button style={{ 
                padding: '0.5rem 1rem', 
                backgroundColor: '#24292e', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer'
              }}>
                Sign Up
              </button>
            </SignUpButton>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div style={{ padding: '2rem', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f0f9ff' }}>
          <h2>🎉 You're signed in!</h2>
          <p>Clerk authentication is working correctly.</p>
        </div>
      </SignedIn>
    </main>
  )
}
```

## Setup Instructions

After applying these changes, follow these steps:

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create a Clerk account and application:**
   - Go to https://dashboard.clerk.com
   - Create a new application
   - Copy your API keys

3. **Create `.env.local` file:**
   ```bash
   cp .env.example .env.local
   ```

4. **Add your Clerk keys to `.env.local`:**
   ```
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
   CLERK_SECRET_KEY=sk_test_xxxxx
   ```

5. **Run the development server:**
   ```bash
   npm run dev
   ```

6. **Visit http://localhost:3000** and test the authentication!

## What's Been Added

- **ClerkProvider**: Wraps the entire application in `app/layout.tsx` to provide authentication context
- **Clerk Components**: Added `SignInButton`, `SignUpButton`, `UserButton`, `SignedIn`, and `SignedOut` to the home page
- **Environment Variables**: Configured `.env.example` with required Clerk keys
- **Package Dependency**: Added `@clerk/nextjs` version 5.0.0 to `package.json`

The application now has a fully functional authentication system with sign-in/sign-up modals and a user button for signed-in users!