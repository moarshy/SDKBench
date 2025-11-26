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
import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'

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

After updating these files, follow these steps:

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
   - Replace the placeholder values with your actual keys from the Clerk dashboard

5. **Run the development server:**
   ```bash
   npm run dev
   ```

6. **Test the authentication:**
   - Visit http://localhost:3000
   - Click "Sign In" or "Sign Up" to test the authentication flow

## What Changed

1. **package.json**: Added `@clerk/nextjs` v5.0.0 dependency
2. **.env.example**: Added required Clerk environment variables with examples
3. **app/layout.tsx**: Wrapped the application with `ClerkProvider` to provide authentication context throughout the app
4. **app/page.tsx**: Added Clerk UI components to demonstrate authentication:
   - `SignedIn`/`SignedOut`: Conditional rendering based on auth state
   - `SignInButton`/`SignUpButton`: Trigger authentication flows
   - `UserButton`: Display user profile and sign-out option

The application is now ready to use Clerk authentication! 🎉