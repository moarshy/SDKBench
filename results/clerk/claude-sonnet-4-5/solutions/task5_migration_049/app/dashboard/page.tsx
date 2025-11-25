import { auth, currentUser } from "@clerk/nextjs/server"
import { redirect } from "next/navigation"

export default async function DashboardPage() {
  const { userId } = auth()
  
  if (!userId) {
    redirect('/sign-in')
  }
  
  const user = await currentUser()
  
  return (
    <div>
      <h1>Welcome, {user?.firstName}!</h1>
    </div>
  )
}

## Testing Checklist

After migration, verify:

- ✅ Public routes (like `/`) are accessible without authentication
- ✅ Protected routes redirect to sign-in when not authenticated
- ✅ Authenticated users can access protected routes
- ✅ API routes respect authentication rules
- ✅ Static files load without authentication checks
- ✅ Sign-in/sign-up flows work correctly

## Migration Complete! 🎉

Your Clerk middleware is now updated to v5. The new approach gives you more flexibility and control over route protection while maintaining the same security level.