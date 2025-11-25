import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server"

const isPublicRoute = createRouteMatcher([
  '/',
])

const isPublicApiRoute = createRouteMatcher([
  '/api/public(.*)',
])

export default clerkMiddleware((auth, request) => {
  const { userId, redirectToSignIn } = auth()
  
  // Allow public routes
  if (isPublicRoute(request) || isPublicApiRoute(request)) {
    return
  }
  
  // Protect all other routes
  if (!userId) {
    return redirectToSignIn()
  }
})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}

## Environment Variables

Ensure your `.env.local` file has the correct variables: