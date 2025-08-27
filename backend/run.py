# backend/run.py
"""
Development server runner
Run with: python run.py
"""

import uvicorn
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Import settings to check configuration
    try:
        from app.core.config import settings
        print(f"🐱 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        print(f"📍 Environment: {settings.ENVIRONMENT}")
        print(f"🔧 Debug mode: {settings.DEBUG}")
        print(f"📊 Database: {settings.DATABASE_URL}")
        print("-" * 50)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )