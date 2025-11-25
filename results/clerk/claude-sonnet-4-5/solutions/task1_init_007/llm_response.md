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
                cursor: 'pointer',
                backgroundColor: '#0070f3',
                color: 'white',
                border: 'none',
                borderRadius: '5px'
              }}>
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button style={{ 
                padding: '0.75rem 1.5rem', 
                fontSize: '1rem',
                cursor: 'pointer',
                backgroundColor: '#24292e',
                color: 'white',
                border: 'none',
                borderRadius: '5px'
              }}>
                Sign Up
              </button>
            </SignUpButton>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div style={{ padding: '2rem', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
          <h2>🎉 You're signed in!</h2>
          <p>Clerk authentication is now working in your Next.js application.</p>
          <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
            Click on your profile picture in the top right to manage your account.
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

2. **Create a `.env.local` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env.local
   ```

3. **Get your Clerk keys:**
   - Go to https://dashboard.clerk.com
   - Create a new application (or use an existing one)
   - Copy your Publishable Key and Secret Key
   - Paste them into `.env.local`

4. **Run the development server:**
   ```bash
   npm run dev
   ```

5. **Visit http://localhost:3000** and test the authentication!

## What's Been Added

- **ClerkProvider**: Wraps the entire application in `app/layout.tsx` to provide authentication context
- **Clerk Components**: Added `SignInButton`, `SignUpButton`, `UserButton`, `SignedIn`, and `SignedOut` to the home page
- **Environment Variables**: Template for required Clerk API keys
- **User Interface**: Basic UI showing different content for signed-in and signed-out users

The application is now ready with Clerk authentication! Users can sign in/up using the modal dialogs, and signed-in users will see their profile button.