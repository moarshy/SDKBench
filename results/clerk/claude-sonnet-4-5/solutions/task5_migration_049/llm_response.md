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
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
}
```

## Key Changes in Clerk v5 Migration:

### 1. **Import Changes**
- **v4**: `import { authMiddleware } from "@clerk/nextjs"`
- **v5**: `import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server"`

### 2. **Middleware Function**
- **v4**: `authMiddleware()` with configuration object
- **v5**: `clerkMiddleware()` with callback function that receives `auth` and `request`

### 3. **Public Routes Handling**
- **v4**: `publicRoutes` array in configuration
- **v5**: Use `createRouteMatcher()` to define route patterns, then check in middleware callback

### 4. **Protection Logic**
- **v4**: Routes not in `publicRoutes` were automatically protected
- **v5**: Explicitly call `auth().protect()` for routes that should be protected

### Additional Notes:

If you need more advanced configurations, here are some common patterns:

**Multiple public routes:**
```typescript
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)'
])
```

**Ignored routes (completely bypass Clerk):**
```typescript
const isIgnoredRoute = createRouteMatcher([
  '/api/webhook(.*)',
  '/api/public(.*)'
])

export default clerkMiddleware((auth, request) => {
  if (isIgnoredRoute(request)) return
  
  if (!isPublicRoute(request)) {
    auth().protect()
  }
})
```

**Custom redirect after sign-in:**
```typescript
export default clerkMiddleware((auth, request) => {
  if (!isPublicRoute(request)) {
    auth().protect({
      unauthenticatedUrl: '/sign-in',
      unauthorizedUrl: '/unauthorized'
    })
  }
})
```

The migration is now complete and your middleware will work with Clerk v5!