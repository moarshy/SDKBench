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
import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'

export default function Home() {
  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Welcome to Next.js with Clerk</h1>
      
      <SignedOut>
        <div style={{ marginTop: '2rem' }}>
          <p>This app uses Clerk authentication. Please sign in to continue.</p>
          <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
            <SignInButton mode="modal">
              <button style={{ 
                padding: '0.5rem 1rem', 
                backgroundColor: '#6C47FF', 
                color: 'white', 
                border: 'none', 
                borderRadius: '6px',
                cursor: 'pointer'
              }}>
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button style={{ 
                padding: '0.5rem 1rem', 
                backgroundColor: '#17171A', 
                color: 'white', 
                border: 'none', 
                borderRadius: '6px',
                cursor: 'pointer'
              }}>
                Sign Up
              </button>
            </SignUpButton>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div style={{ marginTop: '2rem' }}>
          <p>You are signed in! 🎉</p>
          <div style={{ marginTop: '1rem' }}>
            <UserButton afterSignOutUrl="/" />
          </div>
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

6. **Visit http://localhost:3000** to see your app with Clerk authentication!

## What Changed

1. **package.json**: Added `@clerk/nextjs` v5.0.0 dependency
2. **.env.example**: Added required Clerk environment variables with examples
3. **app/layout.tsx**: Wrapped the application with `ClerkProvider` to provide authentication context throughout the app
4. **app/page.tsx**: Added Clerk components to demonstrate authentication:
   - `SignedIn`/`SignedOut`: Conditionally render content based on auth state
   - `SignInButton`/`SignUpButton`: Trigger authentication flows
   - `UserButton`: Display user profile and sign-out option

The application is now ready with Clerk authentication! Users can sign in/up and the app will automatically manage their session.