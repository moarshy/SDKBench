export {}

declare global {
  interface CustomJwtSessionClaims {
    metadata: {
      role?: 'admin' | 'user'
    }
  }
}

## Setup Instructions:

1. **Install dependencies:**