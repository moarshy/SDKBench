import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)',
  '/api/webhooks(.*)',
])

// Define routes that should be publicly accessible even if signed in
const isIgnoredRoute = createRouteMatcher([
  '/api/public(.*)',
  '/api/webhooks(.*)',
])

export default clerkMiddleware((auth, request) => {
  // Allow public routes to be accessed without authentication
  if (isPublicRoute(request)) {
    return
  }

  // Protect all other routes
  auth().protect()
})

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}