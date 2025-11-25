const cors = require('cors');

// CORS configuration for frontend integration
const corsOptions = {
  origin: process.env.FRONTEND_URL || 'http://localhost:3001',
  credentials: true,
  optionsSuccessStatus: 200
};

module.exports = cors(corsOptions);