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

## Step 8: Create a Protected Dashboard Example