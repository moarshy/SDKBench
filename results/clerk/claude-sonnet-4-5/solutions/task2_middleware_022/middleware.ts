import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)',
  '/api/webhooks(.*)',
])

// Define routes that should be publicly accessible even when signed in
const isIgnoredRoute = createRouteMatcher([
  '/api/health',
  '/api/status',
])

export default clerkMiddleware(async (auth, request) => {
  // Allow ignored routes to pass through without any checks
  if (isIgnoredRoute(request)) {
    return
  }

  // Protect all routes that are not public
  if (!isPublicRoute(request)) {
    await auth.protect()
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