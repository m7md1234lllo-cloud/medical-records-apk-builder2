"""
Flask Background Service for Android
خدمة Flask في الخلفية
"""

import os
import sys
from time import sleep

# Add app directory to path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Android service
from jnius import autoclass

PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService

def start_flask():
    """Start Flask server"""
    try:
        from app import app, init_db
        
        # Initialize database
        init_db()
        
        print("Flask Service: Starting server on 127.0.0.1:5000")
        
        # Run Flask
        app.run(
            host='127.0.0.1',
            port=5000,
            threaded=True,
            use_reloader=False,
            debug=False
        )
    except Exception as e:
        print(f"Flask Service Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Flask Service: Starting...")
    start_flask()
