import os
import sys

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

# Custom ASGI wrapper to resolve requested path from Vercel headers
async def handler(scope: Scope, receive: Receive, send: Send):
    if scope["type"] == "http":
        headers = dict(scope.get("headers", []))
        matched_path = headers.get(b"x-matched-path", b"").decode("latin1")
        forwarded_uri = headers.get(b"x-forwarded-uri", b"").decode("latin1")
        
        if matched_path and matched_path not in ["/api/index.py", "/api/index", "/api"]:
            scope["path"] = matched_path.split("?")[0]
        elif forwarded_uri and forwarded_uri not in ["/api/index.py", "/api/index", "/api"]:
            scope["path"] = forwarded_uri.split("?")[0]

    await app(scope, receive, send)

# Assign handler as default callable
app = handler
