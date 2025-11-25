import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

// Define which routes should be protected
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/api/protected(.*)',
  // Add more protected routes here as needed
  // '/admin(.*)',
  // '/settings(.*)',
])

// Define public routes (optional - for explicit public route handling)
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)',
  // Add more public routes here
])

export default clerkMiddleware((auth, req) => {
  // Get the authentication state
  const { userId } = auth()
  
  // If the route is protected and user is not authenticated, redirect to sign-in
  if (isProtectedRoute(req)) {
    if (!userId) {
      // Get the sign-in URL
      const signInUrl = new URL('/sign-in', req.url)
      // Add the redirect URL as a query parameter to return after sign-in
      signInUrl.searchParams.set('redirect_url', req.url)
      return NextResponse.redirect(signInUrl)
    }
  }

  // Allow the request to proceed
  return NextResponse.next()
})

export const config = {
  // Match all routes except static files and internal Next.js routes
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}