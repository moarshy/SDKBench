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
        
    The connection is stored in Flask's g object to ensure
    one connection per request context.
    """
    if 'db' not in g:
        try:
            # Create directory if it doesn't exist
            db_path = app.config['LANCEDB_PATH']
            os.makedirs(db_path, exist_ok=True)
            
            # Initialize LanceDB connection
            g.db = lancedb.connect(db_path)
            app.logger.info(f"Connected to LanceDB at {db_path}")
        except Exception as e:
            app.logger.error(f"Failed to connect to LanceDB: {e}")
            raise
    
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection at the end of request."""
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

@app.route('/tables')
def list_tables():
    """List all tables in the database."""
    try:
        db = get_db()
        tables = db.table_names()
        return {
            'tables': tables,
            'count': len(tables)
        }, 200
    except Exception as e:
        app.logger.error(f"Failed to list tables: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }, 500

def init_db():
    """Initialize database with app context."""
    with app.app_context():
        try:
            db = get_db()
            app.logger.info("Database initialized successfully")
            app.logger.info(f"Existing tables: {db.table_names()}")
            return db
        except Exception as e:
            app.logger.error(f"Database initialization failed: {e}")
            raise

def main():
    """Initialize and verify the Flask application."""
    print("Initializing Flask app with LanceDB...")
    
    # Initialize database
    try:
        db = init_db()
        print(f"✓ Database connected at: {app.config['LANCEDB_PATH']}")
        print(f"✓ Existing tables: {db.table_names()}")
        print("✓ Flask app ready")
        
        # Run the app in debug mode
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        raise

if __name__ == "__main__":
    main()