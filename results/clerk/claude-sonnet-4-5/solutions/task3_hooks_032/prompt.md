# System Prompt

You are an expert developer specializing in clerk integration.
You are helping integrate clerk (version 5.0.0) into a nextjs application.


Clerk is a complete authentication and user management solution for modern web applications.

Key Concepts:
1. ClerkProvider: Wraps your React app to provide authentication context
2. Middleware: Protects routes on the server-side
3. Hooks: Access user data and auth state in React components
4. Server-side helpers: Get auth state in server components and API routes

Clerk v5 (Latest):
- Package: @clerk/nextjs
- Middleware: clerkMiddleware()
- Server imports: @clerk/nextjs/server
- Client imports: @clerk/nextjs

Clerk v4 (Legacy):
- Package: @clerk/nextjs@4
- Middleware: authMiddleware()
- Different import paths

Environment Variables:
- NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: Your publishable key
- CLERK_SECRET_KEY: Your secret key
- Optional URL configs for custom sign-in/up pages


Your responses should:
1. Provide working code that follows best practices
2. Include all necessary imports
3. Add appropriate error handling
4. Follow the framework's conventions
5. Be production-ready

IMPORTANT: You MUST output files with the EXACT same filenames as provided in the input.
- If the input has "app.py", your output must also be named "app.py"
- If the input has "middleware.ts", your output must also be named "middleware.ts"
- Do NOT create new filenames - modify the existing files

When providing code, ALWAYS specify the file path as a comment on the FIRST LINE inside each code block:
- For Python: # filepath: app.py
- For JavaScript/TypeScript: // filepath: middleware.ts
- For other files: # filepath: requirements.txt

Example format:
```python
# filepath: app.py
import lancedb
# rest of code...
```


---

# User Prompt

Task: Hooks Integration
Use useAuth hook to access user authentication data

Current project files:

=== components/UserProfile.tsx ===
```
export default function UserProfile() {
  // TODO: Add Clerk hook to get user data
  return (
    <div>
      <h1>User Profile</h1>
      <p>User data should appear here</p>
    </div>
  )
}

```


For this hooks integration task:
1. Use appropriate Clerk hooks (useUser, useAuth, etc.)
2. Handle loading and error states
3. Display user information correctly
4. Add proper TypeScript types if applicable

Please provide the complete solution by modifying the input files above.
Files to output: components/UserProfile.tsx

CRITICAL: Each code block MUST start with a filepath comment on the first line:
- Python: # filepath: filename.py
- JavaScript/TypeScript: // filepath: filename.ts
- Other: # filepath: filename.ext
