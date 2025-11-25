import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: '#f8f9fa'
    }}>
      <SignIn 
        appearance={{
          elements: {
            rootBox: 'mx-auto',
            card: 'shadow-lg'
          }
        }}
      />
    </div>
  )
}

### 7. Sign Up Page