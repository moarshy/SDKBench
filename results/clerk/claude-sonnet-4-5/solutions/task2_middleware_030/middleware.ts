import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
  '/api/public(.*)',
])

// Define routes that should be publicly accessible even if signed in
const isPublicApiRoute = createRouteMatcher([
  '/api/public(.*)',
])

export default clerkMiddleware(async (auth, request) => {
  // Get the authentication state
  const { userId } = await auth()

  // If the route is not public and user is not authenticated, protect it
  if (!isPublicRoute(request) && !userId) {
    // This will redirect to sign-in page
    return await auth.protect()
  }

  // Optional: Add custom logic for authenticated users
  // For example, redirect authenticated users away from auth pages
  const url = request.nextUrl
  if (userId && (url.pathname.startsWith('/sign-in') || url.pathname.startsWith('/sign-up'))) {
    return Response.redirect(new URL('/dashboard', request.url))
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