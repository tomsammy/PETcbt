import os
import sys
import webbrowser
import threading
import time
import uvicorn

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from parser import seed_database
from database import init_db

def open_browser():
    time.sleep(1.5)
    url = "http://127.0.0.1:8000"
    print("=======================================================")
    print(f"Kwara State CBT Portal is live at: {url}")
    print("Opening browser automatically...")
    print("=======================================================")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")

def main():
    print("Initializing Kwara State Civil Service CBT System...")
    init_db()
    seed_database()
    
    # Start browser opener thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run FastAPI server with Uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="info", reload=False)

if __name__ == "__main__":
    main()
