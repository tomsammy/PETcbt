import os
import sys
import urllib.parse

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
app_dir = os.path.join(root_dir, "kwara_cbt_app")

if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from database import init_db, get_db_connection
from parser import seed_database
from app import app
from starlette.types import Scope, Receive, Send

# Initialize database on cold start
try:
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM questions")
    row = c.fetchone()
    if not row or row["cnt"] == 0:
        seed_database()
    conn.close()
except Exception:
    pass

async def handler(scope: Scope, receive: Receive, send: Send):
    if scope["type"] == "http":
        headers = dict(scope.get("headers", []))
        route_matches = headers.get(b"x-now-route-matches", b"").decode("latin1")
        matched_path = headers.get(b"x-matched-path", b"").decode("latin1")
        
        real_path = None
        if route_matches:
            for part in route_matches.split("&"):
                if part.startswith("1="):
                    real_path = urllib.parse.unquote(part[2:])
                    break
                    
        if not real_path and matched_path and not matched_path.startswith("/api/index"):
            real_path = urllib.parse.unquote(matched_path)
            
        if real_path:
            scope["path"] = real_path.split("?")[0]
            
    await app(scope, receive, send)

app = handler
