import os
import sys

# Add kwara_cbt_app and root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
app_dir = os.path.join(root_dir, "kwara_cbt_app")

if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from database import init_db
from parser import seed_database
from app import app

# Ensure database is initialized on serverless startup
try:
    init_db()
    # Check if questions exist
    from database import get_db_connection
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM questions")
    row = c.fetchone()
    if not row or row["cnt"] == 0:
        seed_database()
    conn.close()
except Exception as e:
    pass
