#!/usr/bin/env python3
"""Main entry point for the AutonoWrite application."""
import os
from app import create_app
from config_development import config

# Force SQLite database for consistency
os.environ['DATABASE_URL'] = 'sqlite:///app.db'

app = create_app(config)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
