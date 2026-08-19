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
from fastapi.responses import JSONResponse

# Ensure database is initialized
try:
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM questions")
    row = c.fetchone()
    if not row or row["cnt"] == 0:
        seed_database()
    conn.close()
except Exception as e:
    pass

# Custom handler wrapper to inspect & fix paths on Vercel
async def handler(scope: Scope, receive: Receive, send: Send):
    if scope["type"] == "http":
        headers = dict(scope.get("headers", []))
        # Look for headers that contain the real requested path
        # Headers in scope are lowercase byte strings
        path_candidate = None
        for key in [b"x-forwarded-uri", b"x-matched-path", b"x-now-route-matches", b"x-vercel-forwarded-for"]:
            if key in headers:
                val = headers[key].decode("latin1", errors="ignore")
                # If x-now-route-matches has "1=...", extract it
                if b"route-matches" in key and "1=" in val:
                    for part in val.split("&"):
                        if part.startswith("1="):
                            path_candidate = "/" + part[2:].lstrip("/")
                elif val.startswith("/"):
                    path_candidate = val
                    
        # Check raw query string for path parameter if present
        query_string = scope.get("query_string", b"").decode("latin1")
        if not path_candidate and "path=" in query_string:
            for qp in query_string.split("&"):
                if qp.startswith("path="):
                    path_candidate = "/" + qp[5:].lstrip("/")

        if path_candidate:
            scope["path"] = path_candidate.split("?")[0]
        else:
            # Fallback based on original scope path
            p = scope.get("path", "")
            if p in ["/api/index.py", "/api/index", "/api/index/"]:
                scope["path"] = "/"
            elif p.startswith("/api/index.py/"):
                scope["path"] = p[len("/api/index.py"):]

    await app(scope, receive, send)
