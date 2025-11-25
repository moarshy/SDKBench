# Clerk Integration Patterns
## Overview
Total repositories analyzed: 20
Analysis date: 2025-11-20

## Frameworks
- **nextjs**: 16 repositories
- **react**: 4 repositories

## Clerk Versions
- `^6.12.7`: 1 repositories
- `^4.21.15`: 1 repositories
- `^6.20.0`: 1 repositories
- `^6.34.0`: 1 repositories
- `^4.6.15`: 1 repositories
- `^0.17.7`: 1 repositories
- `^4.29.6`: 1 repositories
- `workspace:*`: 1 repositories
- `^5.0.0-beta.35`: 1 repositories
- `^6.11.3`: 1 repositories

## Ingredient 1: Initialization Patterns

### Provider Usage
- Total repos with ClerkProvider: 22
- With publishableKey: 0
- With appearance config: 8
- With redirect URLs: 0

### Common Imports
- `import { ClerkProvider } from "@clerk/nextjs"`: 18 repos
- `import { auth } from "@clerk/nextjs/server"`: 18 repos
- `import { currentUser } from "@clerk/nextjs"`: 14 repos
- `import { useUser } from "@clerk/nextjs"`: 10 repos
- `import { dark } from "@clerk/themes"`: 7 repos
- `import { ClerkProvider } from '@clerk/nextjs'`: 7 repos
- `import { clerkMiddleware } from '@clerk/nextjs/server'`: 7 repos
- `import { SignIn } from "@clerk/nextjs"`: 6 repos
- `import { SignUp } from "@clerk/nextjs"`: 5 repos
- `import { auth } from '@clerk/nextjs/server'`: 5 repos

## Ingredient 2: Configuration Patterns

### Environment Variables
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`: 12 repos
- `CLERK_SECRET_KEY`: 12 repos
- `NEXT_PUBLIC_CLERK_SIGN_IN_URL`: 6 repos
- `NEXT_PUBLIC_CLERK_SIGN_UP_URL`: 5 repos
- `CLERK_WEBHOOK_SECRET`: 4 repos
- `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL`: 3 repos
- `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL`: 3 repos
- `NEXT_PUBLIC_CLERK_SIGN_IN_FORCE_REDIRECT_URL`: 2 repos
- `NEXT_PUBLIC_CLERK_SIGN_UP_FORCE_REDIRECT_URL`: 2 repos
- `CLERK_SIGN_UP_FALLBACK_URL`: 1 repos

## Ingredient 3: Integration Points

### Middleware Usage
- authMiddleware: 5 repos
- express_middleware: 0 repos

### Hook Usage
- `useUser()`: 23 repos
- `useAuth()`: 15 repos
- `useClerk()`: 4 repos
- `useSignIn()`: 4 repos
- `useSignUp()`: 4 repos

### API Protection Methods
- uses_get_auth: 6 repos
- uses_current_user: 2 repos

## Task Suitability

### task1_init
Found 22 suitable repositories
- clerk/clerk-playwright-nextjs
- adrianhajdin/threads
- adrianhajdin/threads
- nextify-limited/saasfly
- adrianhajdin/ai_saas_app
- ... and 17 more

### task2_middleware
Found 5 suitable repositories
- adrianhajdin/threads
- vercel/next-forge
- adrianhajdin/ai_saas_app
- hardikverma22/travel-planner-ai
- vanxh/openbio

### task3_hooks
Found 39 suitable repositories
- nextify-limited/saasfly
- nextify-limited/saasfly
- nextify-limited/saasfly
- chen-rn/CUA
- chen-rn/CUA
- ... and 34 more

### task4_complete
Found 4 suitable repositories
- adrianhajdin/threads
- nextify-limited/saasfly
- adrianhajdin/collaborative-editor
- vanxh/openbio

### task5_migration
Found 4 suitable repositories
- adrianhajdin/threads
- chen-rn/CUA
- adrianhajdin/ai_saas_app
- vanxh/openbio
