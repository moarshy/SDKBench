# filepath: app.py
"""Flask application with LanceDB."""

import os
from flask import Flask, g
import lancedb

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['LANCEDB_PATH'] = os.environ.get('LANCEDB_PATH', './data/lancedb')

def get_db():
    """Get database connection.
    
    Returns:
        lancedb.DBConnection: Database connection instance
        
    This function ensures a single database connection per request context.
    The connection is stored in Flask's g object and reused within the same request.
    """
    if 'db' not in g:
        try:
            # Create directory if it doesn't exist
            db_path = app.config['LANCEDB_PATH']
            os.makedirs(db_path, exist_ok=True)
            
            # Initialize database connection
            g.db = lancedb.connect(db_path)
            app.logger.info(f"Connected to LanceDB at {db_path}")
        except Exception as e:
            app.logger.error(f"Failed to connect to LanceDB: {e}")
            raise
    
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection at the end of request.
    
    Args:
        error: Any error that occurred during request processing
    """
    db = g.pop('db', None)
    if db is not None:
        # LanceDB connections don't need explicit closing
        # but we remove it from the context
        app.logger.debug("Database connection removed from context")

@app.route('/')
def index():
    """Health check endpoint."""
    try:
        db = get_db()
        # List tables to verify connection
        tables = db.table_names()
        return {
            'status': 'ok',
            'message': 'Flask app with LanceDB is running',
            'database_path': app.config['LANCEDB_PATH'],
            'tables': tables
        }, 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }, 500

@app.route('/health')
def health():
    """Detailed health check endpoint."""
    try:
        db = get_db()
        tables = db.table_names()
        
        return {
            'status': 'healthy',
            'database': {
                'connected': True,
                'path': app.config['LANCEDB_PATH'],
                'tables_count': len(tables),
                'tables': tables
            }
        }, 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'database': {
                'connected': False,
                'error': str(e)
            }
        }, 503

def init_db():
    """Initialize database with sample data (optional).
    
    This function can be called to set up initial tables or data.
    """
    with app.app_context():
        try:
            db = get_db()
            app.logger.info("Database initialized successfully")
            app.logger.info(f"Available tables: {db.table_names()}")
        except Exception as e:
            app.logger.error(f"Database initialization failed: {e}")
            raise

def main():
    """Main entry point for testing."""
    print("Flask app ready")
    
    # Test database connection
    with app.app_context():
        try:
            db = get_db()
            print(f"✓ Successfully connected to LanceDB at {app.config['LANCEDB_PATH']}")
            print(f"✓ Available tables: {db.table_names()}")
        except Exception as e:
            print(f"✗ Failed to connect to LanceDB: {e}")
            return
    
    print("\nStarting Flask development server...")
    print("Visit http://127.0.0.1:5000/ for health check")
    print("Visit http://127.0.0.1:5000/health for detailed status")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()