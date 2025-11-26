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
   - Clerk v5 consolidated server-side imports into the `/server` path
   - The `/app-beta` path was removed as App Router is now stable

### What Stayed the Same:

- The `currentUser()` function signature and usage remains identical
- User object structure and properties are unchanged
- Component logic requires no modifications

### Additional Notes:

- This is a straightforward import path migration
- No changes to environment variables are needed
- The function continues to work as a server component
- All user properties (`firstName`, `emailAddresses`, etc.) remain accessible in the same way

If you have other Clerk v4 server-side utilities in your project (like `auth()`, `clerkClient`, etc.), they should also be imported from `@clerk/nextjs/server` in v5.