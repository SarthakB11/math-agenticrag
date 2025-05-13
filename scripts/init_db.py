#!/usr/bin/env python3
"""
Script to initialize the database tables for the Math Agent
"""
import os
import sys
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Initialize the database tables"""
    try:
        logger.info("Initializing database tables...")
        init_db()
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 