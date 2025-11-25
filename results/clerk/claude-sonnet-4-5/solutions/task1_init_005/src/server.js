const app = require('./app');

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`Clerk integration: ${process.env.CLERK_PUBLISHABLE_KEY ? 'Configured' : 'Not configured'}`);
});

### 4. Frontend HTML (with Clerk Components)