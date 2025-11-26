import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}

## Middleware

The application uses Clerk's Express middleware:
- `clerkMiddleware()` - Initializes Clerk authentication context
- `requireAuth()` - Protects routes requiring authentication

## Error Handling

The application includes:
- Global error handler for uncaught errors
- 404 handler for undefined routes
- Try-catch blocks in async route handlers

## Security Best Practices

1. Never commit `.env` file to version control
2. Use environment variables for all sensitive data
3. Keep your Clerk Secret Key secure
4. Use HTTPS in production
5. Implement rate limiting for production use

## Additional Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk Express SDK](https://clerk.com/docs/references/express/overview)
- [Express.js Documentation](https://expressjs.com/)