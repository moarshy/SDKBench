I'll help you initialize Clerk authentication in your Express application. Since you mentioned this is an Express app but the instructions reference React/Next.js patterns, I'll provide a proper Express integration with Clerk.

```javascript
// filepath: app.js
const express = require('express');
const { ClerkExpressRequireAuth, ClerkExpressWithAuth } = require('@clerk/clerk-sdk-node');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Public routes (no authentication required)
app.get('/', (req, res) => {
  res.json({ 
    message: 'Welcome to the API',
    status: 'public'
  });
});

app.get('/api/public', (req, res) => {
  res.json({ 
    message: 'This is a public endpoint',
    timestamp: new Date().toISOString()
  });
});

// Protected routes (authentication required)
app.get('/api/protected', ClerkExpressRequireAuth(), (req, res) => {
  const { userId, sessionId } = req.auth;
  res.json({ 
    message: 'This is a protected endpoint',
    userId,
    sessionId,
    timestamp: new Date().toISOString()
  });
});

// Optional authentication (user data available if authenticated)
app.get('/api/optional', ClerkExpressWithAuth(), (req, res) => {
  const { userId } = req.auth;
  
  if (userId) {
    res.json({ 
      message: 'You are authenticated',
      userId,
      timestamp: new Date().toISOString()
    });
  } else {
    res.json({ 
      message: 'You are not authenticated, but that\'s okay',
      timestamp: new Date().toISOString()
    });
  }
});

// Get current user information
app.get('/api/me', ClerkExpressRequireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    const { clerkClient } = require('@clerk/clerk-sdk-node');
    
    const user = await clerkClient.users.getUser(userId);
    
    res.json({
      id: user.id,
      email: user.emailAddresses[0]?.emailAddress,
      firstName: user.firstName,
      lastName: user.lastName,
      username: user.username,
      imageUrl: user.imageUrl
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to fetch user data',
      message: error.message 
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  
  // Clerk authentication errors
  if (err.status === 401) {
    return res.status(401).json({ 
      error: 'Unauthorized',
      message: 'Authentication required'
    });
  }
  
  res.status(err.status || 500).json({ 
    error: 'Internal Server Error',
    message: err.message 
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ 
    error: 'Not Found',
    message: 'The requested resource does not exist'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`Clerk configured: ${!!process.env.CLERK_SECRET_KEY}`);
});

module.exports = app;
```

```javascript
// filepath: package.json
{
  "name": "clerk-express-app",
  "version": "1.0.0",
  "description": "Express application with Clerk authentication",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js",
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [
    "express",
    "clerk",
    "authentication"
  ],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "@clerk/clerk-sdk-node": "^5.0.0",
    "express": "^4.18.2",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

```bash
# filepath: .env.example
# Clerk Configuration
CLERK_SECRET_KEY=sk_test_your_secret_key_here
CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Server Configuration
PORT=3000
NODE_ENV=development

# Optional: Custom Clerk URLs (if using custom domains)
# CLERK_API_URL=https://api.clerk.com
# CLERK_FRONTEND_API=your-frontend-api.clerk.accounts.dev
```

```markdown
# filepath: README.md
# Clerk Express Authentication

This is an Express.js application integrated with Clerk authentication (v5.0.0).

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Add your Clerk keys from the [Clerk Dashboard](https://dashboard.clerk.com)
   ```bash
   cp .env.example .env
   ```

3. **Get your Clerk keys:**
   - Sign up at [clerk.com](https://clerk.com)
   - Create a new application
   - Copy your `CLERK_SECRET_KEY` and `CLERK_PUBLISHABLE_KEY`
   - Paste them into your `.env` file

4. **Run the application:**
   ```bash
   # Development mode with auto-reload
   npm run dev
   
   # Production mode
   npm start
   ```

## API Endpoints

### Public Endpoints (No Authentication Required)

- `GET /` - Welcome message
- `GET /api/public` - Public data endpoint

### Protected Endpoints (Authentication Required)

- `GET /api/protected` - Returns user ID and session info
- `GET /api/me` - Returns current user's profile information

### Optional Authentication

- `GET /api/optional` - Works with or without authentication

## Authentication

### Client-Side Integration

To authenticate requests from your frontend, include the Clerk session token in the Authorization header:

```javascript
const response = await fetch('http://localhost:3000/api/protected', {
  headers: {
    'Authorization': `Bearer ${await clerk.session.getToken()}`
  }
});
```

### Using with React/Next.js Frontend

Install Clerk in your frontend:

```bash
npm install @clerk/nextjs
# or for React
npm install @clerk/clerk-react
```

Example React component:

```javascript
import { useAuth } from '@clerk/clerk-react';

function ProtectedComponent() {
  const { getToken } = useAuth();
  
  const fetchProtectedData = async () => {
    const token = await getToken();
    const response = await fetch('http://localhost:3000/api/protected', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.json();
  };
  
  // ... rest of component
}
```

## Middleware Usage

### ClerkExpressRequireAuth()
Requires authentication. Returns 401 if not authenticated.

```javascript
app.get('/api/protected', ClerkExpressRequireAuth(), (req, res) => {
  const { userId } = req.auth;
  // Handle authenticated request
});
```

### ClerkExpressWithAuth()
Optional authentication. Provides auth data if available.

```javascript
app.get('/api/optional', ClerkExpressWithAuth(), (req, res) => {
  const { userId } = req.auth;
  if (userId) {
    // User is authenticated
  } else {
    // User is not authenticated
  }
});
```

## Error Handling

The application includes comprehensive error handling:
- 401 Unauthorized for authentication failures
- 404 Not Found for invalid routes
- 500 Internal Server Error for server issues

## Testing

Test the endpoints using curl:

```bash
# Public endpoint
curl http://localhost:3000/api/public

# Protected endpoint (will fail without token)
curl http://localhost:3000/api/protected

# Protected endpoint with token
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:3000/api/protected
```

## Security Best Practices

1. Never commit `.env` file to version control
2. Use HTTPS in production
3. Rotate your Clerk secret keys regularly
4. Implement rate limiting for production
5. Add CORS configuration for frontend integration

## Additional Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk Express SDK](https://clerk.com/docs/references/nodejs/overview)
- [Express.js Documentation](https://expressjs.com/)
```

```javascript
// filepath: middleware/cors.js
const cors = require('cors');

// CORS configuration for frontend integration
const corsOptions = {
  origin: process.env.FRONTEND_URL || 'http://localhost:3001',
  credentials: true,
  optionsSuccessStatus: 200
};

module.exports = cors(corsOptions);
```

```javascript
// filepath: routes/auth.js
const express = require('express');
const { ClerkExpressRequireAuth } = require('@clerk/clerk-sdk-node');
const { clerkClient } = require('@clerk/clerk-sdk-node');
const router = express.Router();

// Get current user
router.get('/me', ClerkExpressRequireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    const user = await clerkClient.users.getUser(userId);
    
    res.json({
      id: user.id,
      email: user.emailAddresses[0]?.emailAddress,
      firstName: user.firstName,
      lastName: user.lastName,
      username: user.username,
      imageUrl: user.imageUrl,
      createdAt: user.createdAt,
      updatedAt: user.updatedAt
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to fetch user data',
      message: error.message 
    });
  }
});

// Update user metadata
router.patch('/me', ClerkExpressRequireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    const { publicMetadata, privateMetadata } = req.body;
    
    const user = await clerkClient.users.updateUser(userId, {
      publicMetadata,
      privateMetadata
    });
    
    res.json({
      message: 'User updated successfully',
      user: {
        id: user.id,
        publicMetadata: user.publicMetadata,
        updatedAt: user.updatedAt
      }
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to update user',
      message: error.message 
    });
  }
});

// Get user sessions
router.get('/sessions', ClerkExpressRequireAuth(), async (req, res) => {
  try {
    const { userId } = req.auth;
    const sessions = await clerkClient.users.getUserList({ userId });
    
    res.json({
      sessions: sessions.map(session => ({
        id: session.id,
        status: session.status,
        lastActiveAt: session.lastActiveAt,
        expireAt: session.expireAt
      }))
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to fetch sessions',
      message: error.message 
    });
  }
});

module.exports = router;
```

This complete solution provides:

1. **Express app with Clerk integration** - Full authentication setup
2. **Multiple endpoint types** - Public, protected, and optional auth
3. **User management** - Get and update user data
4. **Error handling** - Comprehensive error middleware
5. **Environment configuration** - Proper setup with .env
6. **Documentation** - Complete README with examples
7. **Modular structure** - Separate routes and middleware

To use this:
1. Run `npm install` to install dependencies
2. Copy `.env.example` to `.env` and add your Clerk keys
3. Run `npm run dev` to start the server
4. Test endpoints with curl or integrate with a frontend