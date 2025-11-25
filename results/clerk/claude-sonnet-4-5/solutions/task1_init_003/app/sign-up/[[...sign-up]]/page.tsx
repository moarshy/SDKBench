import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh' 
    }}>
      <SignUp />
    </div>
  )
}

## Step 9: Create a Protected Route Example