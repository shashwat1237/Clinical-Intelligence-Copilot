import sys
import traceback
import os

# 1. Force unbuffered output directly in the script
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("\n" + "="*50, file=sys.stderr)
print("🚀 STARTING DIAGNOSTIC BOOT SEQUENCE 🚀", file=sys.stderr)
print("="*50, file=sys.stderr)

try:
    print("STEP 1: Importing FastAPI...", file=sys.stderr)
    from fastapi import FastAPI
    app = FastAPI(title="Clinical Intelligence Copilot (Diagnostic Mode)")
    
    print("STEP 2: Importing Database Modules...", file=sys.stderr)
    from app.db.session import engine
    from app.db import models_and_crud
    from sqlalchemy import text

    print(f"STEP 3: Attempting to ping database at: {os.environ.get('DATABASE_URL', 'NOT_SET').split('@')[-1]}", file=sys.stderr)
    # We only print the host part of the URL to keep your password secret in the logs
    
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ SUCCESS: Database pinged successfully!", file=sys.stderr)

    print("STEP 4: Attempting to create pgvector extension and tables...", file=sys.stderr)
    with engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
    models_and_crud.Base.metadata.create_all(bind=engine)
    print("✅ SUCCESS: Database tables and vectors initialized!", file=sys.stderr)

    print("STEP 5: Importing Routers...", file=sys.stderr)
    from app.api.v1 import auth, upload, chat, docs_and_reports, search_and_patients, timeline
    
    print("✅ BOOT COMPLETE: Handing over to Uvicorn.", file=sys.stderr)
    print("="*50 + "\n", file=sys.stderr)

except Exception as e:
    # If ANYTHING fails or hangs, this block catches it instantly.
    print("\n" + "!"*50, file=sys.stderr)
    print("🚨 CRITICAL BOOT FAILURE DETECTED 🚨", file=sys.stderr)
    print("!"*50, file=sys.stderr)
    print(f"ERROR TYPE: {type(e).__name__}", file=sys.stderr)
    print(f"ERROR DETAILS: {str(e)}", file=sys.stderr)
    print("\nFULL STACK TRACE:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    print("!"*50 + "\n", file=sys.stderr)
    
    # Force the app to crash instantly so Render doesn't wait 5 minutes
    sys.exit(1)
