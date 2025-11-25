import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)', // Webhook endpoints should be public
  '/api/public(.*)', // Any public API routes
])

// Define routes that should be completely public (no auth check at all)
const isIgnoredRoute = createRouteMatcher([
  '/api/health',
  '/api/status',
])

export default clerkMiddleware((auth, request) => {
  // Skip auth check for ignored routes
  if (isIgnoredRoute(request)) {
    return NextResponse.next()
  }

  // Protect all routes that are not public
  if (!isPublicRoute(request)) {
    auth().protect()
  }

  return NextResponse.next()
})

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}