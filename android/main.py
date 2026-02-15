"""
Medical Records App - Android Version
نظام إدارة الملفات الطبية - نسخة Android
"""

from kivy.app import App
from kivy.uix.widget import Widget
from android.runnable import run_on_ui_thread
from jnius import autoclass, cast
import threading
import time
import os
import sys

# Android classes
PythonActivity = autoclass('org.kivy.android.PythonActivity')
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')

# Add Flask app directory to path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

# Flask server thread
flask_thread = None

def start_flask_server():
    """Start Flask server in background thread"""
    try:
        # Wait a bit for Android to initialize
        time.sleep(2)
        
        # Import Flask app
        from app import app, init_db
        
        # Initialize database
        print("Initializing database...")
        init_db()
        
        # Configure Flask for Android
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        # Start Flask server
        print("Starting Flask server on http://127.0.0.1:5000")
        app.run(
            host='127.0.0.1',
            port=5000,
            threaded=True,
            use_reloader=False,
            debug=False
        )
    except Exception as e:
        print(f"Error starting Flask: {e}")
        import traceback
        traceback.print_exc()

class MedicalRecordsApp(App):
    """Main Android application"""
    
    def build(self):
        """Build the app interface"""
        
        # Start Flask server in background
        global flask_thread
        print("Starting Flask in background...")
        flask_thread = threading.Thread(target=start_flask_server, daemon=True)
        flask_thread.start()
        
        # Wait for Flask to start
        print("Waiting for Flask to initialize...")
        time.sleep(5)
        
        # Create and show WebView
        self.setup_webview()
        
        # Return empty widget (WebView is added natively)
        return Widget()
    
    @run_on_ui_thread
    def setup_webview(self):
        """Setup Android WebView"""
        try:
            # Get current activity
            activity = PythonActivity.mActivity
            
            # Create WebView
            webview = WebView(activity)
            webview.getSettings().setJavaScriptEnabled(True)
            webview.getSettings().setDomStorageEnabled(True)
            webview.getSettings().setDatabaseEnabled(True)
            webview.setWebViewClient(WebViewClient())
            
            # Load Flask app
            webview.loadUrl('http://127.0.0.1:5000')
            
            # Add WebView to activity
            activity.setContentView(webview)
            
            print("WebView loaded successfully!")
            
        except Exception as e:
            print(f"Error setting up WebView: {e}")
            import traceback
            traceback.print_exc()
    
    def on_pause(self):
        """Handle app pause"""
        return True
    
    def on_resume(self):
        """Handle app resume"""
        pass

if __name__ == '__main__':
    print("Starting Medical Records App...")
    MedicalRecordsApp().run()
