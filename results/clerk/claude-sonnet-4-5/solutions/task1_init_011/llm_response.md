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
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <SignInButton mode="modal">
              <button style={{ 
                padding: '0.5rem 1rem', 
                backgroundColor: '#0070f3', 
                color: 'white', 
                border: 'none', 
                borderRadius: '5px',
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
                borderRadius: '5px',
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
   - Create a new application or select an existing one
   - Copy your Publishable Key and Secret Key
   - Paste them into `.env.local`

4. **Run the development server:**
   ```bash
   npm run dev
   ```

5. **Test the authentication:**
   - Visit http://localhost:3000
   - Click "Sign In" or "Sign Up" to test authentication
   - The UserButton will appear when signed in

## What Was Added

1. **ClerkProvider** - Wraps the entire application in `app/layout.tsx` to provide authentication context
2. **Clerk Components** - Added `SignInButton`, `SignUpButton`, `SignedIn`, `SignedOut`, and `UserButton` to the home page
3. **Environment Variables** - Added required Clerk keys to `.env.example`
4. **Package Dependency** - Added `@clerk/nextjs` version 5.0.0 to `package.json`

The application is now ready with Clerk authentication! Users can sign in/up using the modal buttons, and authenticated users will see their profile with the UserButton component.