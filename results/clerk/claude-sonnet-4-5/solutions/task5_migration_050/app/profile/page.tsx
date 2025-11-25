import { currentUser } from '@clerk/nextjs/server'

export default async function Profile() {
  const user = await currentUser()

  if (!user) {
    return <div>Not signed in</div>
  }

  return (
    <div>
      <h1>{user.firstName}</h1>
      <p>{user.emailAddresses[0]?.emailAddress}</p>
    </div>
  )
}

## Migration Summary

### Key Changes Made:

1. **Import Path Update**: Changed from `@clerk/nextjs/app-beta` to `@clerk/nextjs/server`
   - In Clerk v5, all server-side imports (including `currentUser`, `auth`, `clerkClient`) are now imported from `@clerk/nextjs/server`
   - The `/app-beta` path was deprecated and removed in v5

### What Stayed the Same:

- The `currentUser()` function signature and usage remains identical
- The user object structure and properties are unchanged
- No changes needed to the component logic or JSX

### Additional Notes:

This is a straightforward migration for server components. The main breaking change in Clerk v5 for server components is the import path consolidation. All server-side helpers now come from a single import path: `@clerk/nextjs/server`.

If you have other server components or API routes using Clerk, make sure to update their imports as well:
- `auth()` → `@clerk/nextjs/server`
- `clerkClient` → `@clerk/nextjs/server`
- `getAuth()` → `@clerk/nextjs/server` (for Pages Router)