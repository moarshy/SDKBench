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

# Optional: Custom sign-in/sign-up URLs (if you want custom pages)
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
        <div style={{ 
          padding: '2rem', 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px',
          backgroundColor: '#f9fafb'
        }}>
          <h2>Get Started</h2>
          <p>This app uses Clerk authentication. Please sign in to continue.</p>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <SignInButton mode="modal">
              <button style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#2563eb',
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
                padding: '0.5rem 1rem',
                backgroundColor: '#059669',
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
        <div style={{ 
          padding: '2rem', 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px',
          backgroundColor: '#f0fdf4'
        }}>
          <h2>✓ Authentication Active</h2>
          <p>You are successfully signed in with Clerk authentication!</p>
          <p style={{ marginTop: '1rem', color: '#6b7280' }}>
            Your user information is now available throughout the application.
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

3. **Create `.env.local` file:**
   ```bash
   cp .env.example .env.local
   ```
   Then add your actual Clerk keys to `.env.local`

4. **Run the development server:**
   ```bash
   npm run dev
   ```

5. **Test the authentication:**
   - Visit http://localhost:3000
   - Click "Sign In" or "Sign Up" to test authentication
   - The UserButton will appear in the top-right when signed in

## What Was Added

1. **package.json**: Added `@clerk/nextjs` v5.0.0 dependency
2. **.env.example**: Added required Clerk environment variables with examples
3. **app/layout.tsx**: Wrapped the application with `ClerkProvider`
4. **app/page.tsx**: Added Clerk UI components to demonstrate authentication state

The application is now ready with Clerk authentication! Users can sign in/up, and you can use Clerk's hooks and components throughout your app.