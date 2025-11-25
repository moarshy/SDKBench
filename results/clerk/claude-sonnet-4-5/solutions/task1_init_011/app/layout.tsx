import { ClerkProvider } from '@clerk/nextjs'
import './globals.css' // Add this if you have global styles

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

## Step 4: Create Middleware for Route Protection