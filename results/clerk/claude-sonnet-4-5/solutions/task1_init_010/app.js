require('dotenv').config();
const express = require('express');
const { clerkMiddleware, requireAuth } = require('@clerk/express');
const path = require('path');

const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Set view engine (if using server-side rendering)
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Initialize Clerk middleware
// This makes auth state available on all routes via req.auth
app.use(clerkMiddleware());

// Routes
app.use('/', require('./routes/index'));
app.use('/api', require('./routes/api'));
app.use('/dashboard', requireAuth(), require('./routes/dashboard'));

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: {
      message: err.message || 'Internal Server Error',
      status: err.status || 500
    }
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: {
      message: 'Route not found',
      status: 404
    }
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV}`);
});

module.exports = app;

### 3. Public Routes