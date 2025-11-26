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
        <div style={{ padding: '2rem', backgroundColor: '#f3f4f6', borderRadius: '0.5rem' }}>
          <h2>🎉 You're signed in!</h2>
          <p>Clerk authentication is now working in your Next.js application.</p>
          <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#6b7280' }}>
            Click your profile picture in the top right to manage your account.
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
   - Click "Sign In" or "Sign Up"
   - Complete the authentication flow

## What was implemented:

✅ **ClerkProvider** wraps the entire application in `app/layout.tsx`
✅ **Environment variables** configured in `.env.example`
✅ **Clerk components** added to `app/page.tsx`:
  - `SignInButton` - Opens sign-in modal
  - `SignUpButton` - Opens sign-up modal
  - `UserButton` - Shows user profile menu when signed in
  - `SignedIn` - Renders content only for authenticated users
  - `SignedOut` - Renders content only for unauthenticated users

The application is now ready with Clerk authentication! Users can sign in/up and the UI will automatically update based on their authentication state.