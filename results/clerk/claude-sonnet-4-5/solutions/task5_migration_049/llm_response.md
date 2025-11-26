```typescript
// filepath: middleware.ts
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server"

const isPublicRoute = createRouteMatcher(['/'])

export default clerkMiddleware((auth, request) => {
  if (!isPublicRoute(request)) {
    auth().protect()
  }
})

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}
```

## Migration Summary

### Key Changes from Clerk v4 to v5:

1. **Import Changes**:
   - `authMiddleware` → `clerkMiddleware`
   - Added `createRouteMatcher` from `@clerk/nextjs/server`

2. **Middleware Function Signature**:
   - v4: `authMiddleware({ publicRoutes: [...] })`
   - v5: `clerkMiddleware((auth, request) => { ... })`

3. **Public Routes Handling**:
   - v4: Defined via `publicRoutes` config option
   - v5: Use `createRouteMatcher` to define public routes, then conditionally call `auth().protect()` for protected routes

4. **Route Protection**:
   - v4: Automatic protection with `publicRoutes` exclusion
   - v5: Explicit protection using `auth().protect()` for non-public routes

5. **Matcher Configuration**:
   - Updated to the recommended v5 matcher pattern that better handles static files and Next.js internals

### How It Works:

- `createRouteMatcher(['/'])` creates a function that checks if the current route matches any public routes
- Inside `clerkMiddleware`, we check if the route is NOT public
- If it's not public, we call `auth().protect()` to enforce authentication
- Public routes (like '/') will be accessible without authentication

This migration maintains the same functionality as your v4 setup while following Clerk v5's new patterns and best practices.